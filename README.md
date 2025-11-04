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
##Procfile
```bash
web: gunicorn app:app
```

## buildspec.yml
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
## Elastic Beanstalk Setup (One-Time)
1.	Go to AWS Console → Elastic Beanstalk → Create environment → Web server environment
2.	Platform: Python
3.	Application name: pdf-compress
4.	Environment name: pdf-compress-env
5.	Application code: “Sample application” (for first launch)
6.	Roles:
  o	Service role: aws-elasticbeanstalk-service-role
  o	EC2 instance profile: aws-elasticbeanstalk-ec2-role
✅ After creation, confirm that the environment is Green.
________________________________________
🔧 A4. CodeBuild Project
Setting	Value
Source	No source
Artifacts	CodePipeline
Environment	Managed image → Amazon Linux 2 → aws/codebuild/standard:7.0 → Python 3.11
Buildspec	Use the buildspec.yml file (CodeBuild will read it from the input artifact)
Project Name	pdf-compress-build
________________________________________
🔁 A5. CodePipeline Setup
1.	Console → CodePipeline → Create pipeline
2.	Source: GitHub (via your connection) → select repo/branch

3.	Build: Select the pdf-compress-build CodeBuild project

4.	Deploy: Elastic Beanstalk
o	Application name: pdf-compress

o	Environment name: pdf-compress-env

5.	Create pipeline
Once complete, CodePipeline will automatically: - Pull your source from GitHub
- Trigger CodeBuild
- Deploy the artifacts to Elastic Beanstalk
✅ When the pipeline completes successfully, your Beanstalk environment should turn Green.
🌐 Open the environment URL to view your deployed app.
________________________________________
🧩 Summary
This pipeline fully automates: - Building the Python app via CodeBuild
- Packaging & deploying to Elastic Beanstalk
- Continuous delivery from GitHub → CodePipeline → CodeBuild → Beanstalk
