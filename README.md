Beanstalk via CodePipeline + CodeBuild
Gotcha. Here’s the streamlined, end-to-end setup using Option 1 (no manual zip in buildspec).
1. Create a new repo
Create a fresh repo (e.g., pdf-compress-beanstalk-pipeline) with this layout:
.
├─ app.py
├─ requirements.txt
├─ templates/
│  └─ index.html
├─ Procfile
└─ buildspec.yml
Procfile
web: gunicorn app:app
buildspec.yml (Option 1: let CodePipeline package files—no zip step)
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.11
    commands:
      - pip install --upgrade pip
      - pip install -r requirements.txt
  build:
    commands:
      - python -m py_compile app.py

artifacts:
  files:
    - app.py
    - requirements.txt
    - Procfile
    - templates/**/*
Commit & push to your GitHub repo/branch.

2. Elastic Beanstalk (one-time)
a.	AWS Console → Elastic Beanstalk → Create environment → Web server environment
b.	Platform: Python
c.	Application name: pdf-compress
d.	Environment name: pdf-compress-env
e.	Application code: “Sample application” (just for first launch)
f.	Roles:
    o	Service role: aws-elasticbeanstalk-service-role
    o	EC2 instance profile: aws-elasticbeanstalk-ec2-role
   
After creation, confirm the env is Green.
 
3. CodeBuild project
•	Source: No source
•	Artifacts: CodePipeline
•	Environment: Managed image → Amazon Linux 2 → aws/codebuild/standard:7.0 → Python 3.11
•	Buildspec: Use a buildspec file (CodeBuild will read buildspec.yml from the input artifact it receives from the pipeline)
•	Name: pdf-compress-build
 
4. CodePipeline
1.	Console → CodePipeline → Create pipeline
2.	Source: GitHub via your Connection → select repo/branch
3.	Build: pdf-compress-build
4.	Deploy: Elastic Beanstalk
o	Application name: pdf-compress
o	Environment name: pdf-compress-env
5.	Create pipeline → it runs end-to-end → EB shows Green → open the env URL.

 
________________________________________
