## Beanstalk via CodePipeline + CodeBuild
This guide provides a streamlined, end-to-end setup for deploying a Python web app to AWS Elastic Beanstalk using CodePipeline and CodeBuild.
________________________________________
## 1. Create a New Repository
Create a new GitHub repository (e.g., pdf-compress-beanstalk-pipeline) with the following structure:

```bash
├─ app.py
├─ requirements.txt
├─ templates/
│  └─ index.html
├─ Procfile
└─ buildspec.yml
```
### Add a Procfile
```bash
web: gunicorn app:app
```

### Add a Buildspec.yml
Let CodePipeline package files

```bash
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
```

Commit and push to your GitHub repo/branch.
________________________________________
## 2. Elastic Beanstalk Setup (One-Time)
a. Go to **AWS Console** → **Elastic Beanstalk** → *Create environment* → *Web server environment*  
b. Platform: **Python**  
c. Application name: **pdf-compress**  
d. Environment name: **pdf-compress-env**  
e. Application code: “Sample application” (for first launch)  
f. Roles:  
   - Service role: `aws-elasticbeanstalk-service-role`  
   - EC2 instance profile: `aws-elasticbeanstalk-ec2-role`  

After creation, confirm that the environment is **Green**.
________________________________________
## 3. CodeBuild Project
Setting	Value
Source	No source
Artifacts	CodePipeline
Environment	Managed image → Amazon Linux 2 → aws/codebuild/standard:7.0 → Python 3.11
Buildspec	Use the buildspec.yml file (CodeBuild will read it from the input artifact)
Project Name	pdf-compress-build
________________________________________
## 4. CodePipeline Setup
a.	Console → CodePipeline → Create pipeline <br>
b.	Source: GitHub (via your connection) → select repo/branch <br>
c.	Build: Select the pdf-compress-build CodeBuild project <br>
d.	Deploy: Elastic Beanstalk <br>
  - Application name: pdf-compress <br>
  - Environment name: pdf-compress-env <br>

## 5.	Create pipeline
Once complete, CodePipeline will automatically pull your source from GitHub <br>
- Trigger CodeBuild <br>
- Deploy the artifacts to Elastic Beanstalk <br>

When the pipeline completes successfully, your Beanstalk environment should turn Green. Open the environment URL to view your deployed app.
________________________________________
## Summary
This pipeline fully automates building the Python app via CodeBuild
- Packaging & deploying to Elastic Beanstalk <br>
- Continuous delivery from GitHub → CodePipeline → CodeBuild → Beanstalk <br>
