# Example Usage Guide

## Complete Workflow Example

### Step 1: Create Amplify App (Can be Automated!)

#### Option A: Programmatic Setup (Recommended)
```bash
# Prerequisites: 
# 1. Install Amplify GitHub App: https://github.com/apps/aws-amplify-eu-north-1
# 2. Create a GitHub Personal Access Token:
#    - Go to: https://github.com/settings/tokens/new
#    - Select scope: admin:repo_hook
#    - Generate token and save it securely
#    Or use GitHub CLI: gh auth token

# Create the Amplify app and connect to GitHub
aws amplify create-app \
  --name "my-amplify-app" \
  --repository "https://github.com/yourusername/your-repo" \
  --access-token "ghp_yourGitHubPersonalAccessToken" \
  --platform WEB_COMPUTE \
  --region eu-north-1

# Create and connect a branch
aws amplify create-branch \
  --app-id "d1234abcd5678" \  # Use the app ID from create-app output
  --branch-name "main" \
  --no-enable-auto-build \  # Disable auto-build from the start!
  --region eu-north-1
```

#### Option B: Manual Setup (If you prefer the console)
1. Go to AWS Amplify Console
2. Click "New app" → "Host web app"
3. Choose GitHub and authorize access
4. Select your repository and branch
5. Install the Amplify GitHub App when prompted
6. Complete the setup and note your App ID

### Step 2: Set Up Custom Pipeline (Using MCP)

#### If you created the app manually:
```
/setup_custom_pipeline app_id="d1234abcd5678" branch_name="main" repo_path="/Users/you/your-app"
```

#### Or do EVERYTHING in one command (create app + pipeline):
```
/create_app_and_pipeline \
  app_name="my-amplify-app" \
  repository="https://github.com/yourusername/your-repo" \
  access_token="ghp_yourGitHubToken" \
  branch_name="main" \
  repo_path="/Users/you/your-app"
```

This single command will:
1. Create the Amplify app
2. Connect it to your GitHub repository
3. Create the branch with auto-build disabled
4. Set up the custom pipeline (webhook, build spec, GitHub Actions)

### Step 3: Configure GitHub Secrets

Go to your GitHub repository settings:
1. Navigate to Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

### Step 4: Add Build Spec to Repository

Copy the generated `amplify.yml`:
```bash
cp amplify-buildspec-d1234abcd5678.yml /Users/you/your-app/amplify.yml
```

### Step 5: Commit and Push

```bash
cd /Users/you/your-app
git add amplify.yml .github/workflows/
git commit -m "Set up custom Amplify pipeline"
git push origin main
```

## Common Scenarios

### Scenario 1: Multiple Branches

Set up pipelines for different environments:

```
# Production branch
/setup_custom_pipeline app_id="d1234abcd5678" branch_name="main" repo_path="/Users/you/your-app"

# Staging branch
/setup_custom_pipeline app_id="d1234abcd5678" branch_name="staging" repo_path="/Users/you/your-app"

# Development branch
/setup_custom_pipeline app_id="d1234abcd5678" branch_name="develop" repo_path="/Users/you/your-app"
```

### Scenario 2: Webhook-Only Setup

If you're using a different CI/CD system and only need the webhook:

```
/create_webhook app_id="d1234abcd5678" branch_name="main"
```

Then use the webhook URL in your CI/CD system to trigger frontend builds.

### Scenario 3: Checking App Configuration

Before setting up the pipeline, verify your app details:

```
/get_app_info app_id="d1234abcd5678"
```

## Sample amplify.yml for Next.js App

```yaml
version: 1
applications:
  - appRoot: .
    backend:
      phases:
        build:
          commands:
            - npm ci
            - export CI=1
            - npx ampx generate outputs --branch $AWS_BRANCH --app-id $AWS_APP_ID
    frontend:
      phases:
        preBuild:
          commands:
            - npm ci
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: .next
        files:
          - '**/*'
      cache:
        paths:
          - node_modules/**/*
```

## Sample GitHub Actions Workflow

```yaml
name: Amplify Custom Pipeline - main

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy backend with Amplify
        run: |
          export CI=1
          npx ampx pipeline-deploy \
            --branch main \
            --app-id d1234abcd5678
      
      - name: Trigger frontend build
        if: success()
        run: |
          curl -X POST 'https://webhooks.amplify.us-east-1.amazonaws.com/prod/webhooks?id=webhook-id&token=token&operation=startbuild'
```

## Testing Your Pipeline

After setup, test the pipeline:

1. Make a small change to your code
2. Commit and push:
   ```bash
   git add .
   git commit -m "Test custom pipeline"
   git push origin main
   ```
3. Check GitHub Actions tab in your repository
4. Monitor the Amplify Console for frontend build
5. Verify your app is updated

## Troubleshooting Commands

### Check AWS CLI Configuration
```bash
aws configure list
aws amplify list-apps
```

### Test Webhook Manually
```bash
curl -X POST 'your-webhook-url-here'
```

### View GitHub Actions Logs
```bash
gh run list --branch main
gh run view
```

## Advanced: Using with AWS CodePipeline

If you prefer AWS CodePipeline instead of GitHub Actions:

1. Set up the pipeline with MCP to get webhook
2. Create CodePipeline with these stages:
   - Source: GitHub
   - Build: CodeBuild with `npx ampx pipeline-deploy`
   - Deploy: Lambda function to trigger webhook

Example buildspec.yml for CodeBuild:
```yaml
version: 0.2
phases:
  install:
    runtime-versions:
      nodejs: 18
  pre_build:
    commands:
      - npm ci
  build:
    commands:
      - export CI=1
      - npx ampx pipeline-deploy --branch $BRANCH_NAME --app-id $APP_ID
  post_build:
    commands:
      - curl -X POST $WEBHOOK_URL
```