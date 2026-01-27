---
description: Deploy the application to production or staging environments
argument-hint: [environment] (staging/production)
---

# Deployment Command

## Instructions

1.  **Analyze Deployment Context**
    - Check for deployment configuration files:
        - `Dockerfile` / `docker-compose.yml`
        - `vercel.json`
        - `netlify.toml`
        - `fly.toml`
        - `.github/workflows/deploy.yml`
    - Check `package.json` for deploy scripts.
    - Identify the target environment from arguments (default to staging if not specified).

2.  **Pre-Deployment Checks**
    - Run tests: `npm test` or equivalent.
    - Run linters: `npm run lint` or equivalent.
    - Check for uncommitted changes (unless deploying from a clean CI state).
    - Verify all dependencies are installed.

3.  **Execute Deployment**
    - **If Docker/Docker Compose:**
        - Build: `docker build -t app .`
        - Run/Deploy: `docker-compose up -d` or push to registry.
    - **If Vercel/Netlify:**
        - Run `vercel --prod` or `netlify deploy --prod`.
    - **If Script based:**
        - Run `npm run deploy` or `./deploy.sh`.
    - **If Cloud Provider (AWS/Azure/GCP):**
        - Check for Terraform/CDK/CLI tools and execute relevant apply commands.

4.  **Post-Deployment Verification**
    - Check if the service is up and running (Health Check).
    - Verify critical endpoints.
    - Check logs for immediate errors.

5.  **Notification**
    - Summarize the deployment status.
    - Provide the URL of the deployed application.
