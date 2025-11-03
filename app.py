import io
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename  # <-- add this import
import pikepdf
from pikepdf import PdfImage, Name, Stream
from PIL import Image

app = Flask(__name__)
app.secret_key = "pdf-compress-demo"
UPLOAD_DIR = Path(tempfile.gettempdir()) / "pdf_compressor_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _mb(nbytes: int) -> float:
    return round(nbytes / (1024 * 1024), 2)

def _recompress_images(pdf: pikepdf.Pdf, max_side: int, quality: int, grayscale: bool) -> int:
    changed = 0
    for page in pdf.pages:
        resources = page.get("/Resources", None)
        if not resources or "/XObject" not in resources:
            continue
        xobjs = resources["/XObject"]
        for name, xobj in list(xobjs.items()):
            try:
                if "/Subtype" not in xobj or xobj["/Subtype"] != Name("/Image"):
                    continue
                img = PdfImage(xobj)
                pil = img.as_pil_image()
                if grayscale:
                    pil = pil.convert("L")
                else:
                    if pil.mode not in ("RGB", "L"):
                        pil = pil.convert("RGB")
                w, h = pil.size
                scale = min(1.0, max_side / max(w, h)) if max(w, h) > max_side else 1.0
                if scale < 1.0:
                    pil = pil.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
                img_bytes = io.BytesIO()
                pil.save(img_bytes, format="JPEG", quality=quality, optimize=True, progressive=True)
                img_bytes.seek(0)
                colorspace = Name("/DeviceGray") if pil.mode == "L" else Name("/DeviceRGB")
                new_stream = Stream(
                    pdf,
                    img_bytes.getvalue(),
                    Filter=Name("/DCTDecode"),
                    Type=Name("/XObject"),
                    Subtype=Name("/Image"),
                    Width=pil.width,
                    Height=pil.height,
                    ColorSpace=colorspace,
                    BitsPerComponent=8,
                )
                xobjs[name] = new_stream
                changed += 1
            except Exception:
                continue
    return changed

def compress_file(src: Path, dst: Path, max_side: int = 2000, quality: int = 60, grayscale: bool = False):
    with pikepdf.open(str(src)) as pdf:
        changed = _recompress_images(pdf, max_side=max_side, quality=quality, grayscale=grayscale)
        pdf.save(
            str(dst),
            linearize=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            compress_streams=True,
        )
    return changed

@app.route("/")
def home():
    # Provide defaults so the template's {{ form.* }} is always defined
    defaults = {"max_side": 600, "quality": 40, "grayscale": False}
    return render_template("index.html", form=defaults)

@app.route("/compress", methods=["POST"])
def compress():
    file = request.files.get("pdf")
    if not file or file.filename == "":
        flash("Please select a PDF file.")
        return redirect(url_for("home"))

    try:
        max_side = int(request.form.get("max_side", "600"))
        quality = int(request.form.get("quality", "40"))
        grayscale = request.form.get("grayscale") == "on"
    except ValueError:
        flash("Invalid numeric inputs.")
        return redirect(url_for("home"))

    filename = secure_filename(file.filename)
    src_path = UPLOAD_DIR / filename
    file.save(src_path)

    out_name = f"{src_path.stem}.compressed.pdf"
    out_path = UPLOAD_DIR / out_name

    try:
        changed = compress_file(src_path, out_path, max_side=max_side, quality=quality, grayscale=grayscale)
    except Exception as e:
        flash(f"Compression failed: {e}")
        return redirect(url_for("home"))

    orig_size = src_path.stat().st_size
    out_size = out_path.stat().st_size if out_path.exists() else orig_size
    saved_pct = max(0, round((1 - out_size / orig_size) * 100, 1)) if orig_size > 0 else 0

    if changed == 0:
        flash("Note: No embedded images were recompressed (document may be mostly text/vector).")

    result = {
        "orig_name": filename,
        "out_name": out_name,
        "orig_size": _mb(orig_size),
        "out_size": _mb(out_size),
        "saved": saved_pct,
        "out_file": out_name
    }

    # Pass back the user's choices so the form stays "sticky"
    form_state = {"max_side": max_side, "quality": quality, "grayscale": grayscale}
    return render_template("index.html", result=result, form=form_state)

@app.route("/download/<path:filename>")
def download(filename):
    fp = UPLOAD_DIR / filename
    if not fp.exists():
        flash("File not found.")
        return redirect(url_for("home"))
    return send_file(fp, as_attachment=True, download_name=fp.name, mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)
