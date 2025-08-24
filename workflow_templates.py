"""
GitHub Actions Workflow Templates for Different Deployment Modes

This module provides appropriate workflow templates based on the deployment mode:
- Repository-connected apps (most common)
- Manual deployment apps (rare)
"""

def get_repository_connected_workflow(app_id: str, branch_name: str, aws_region: str = 'eu-north-1') -> str:
    """
    Generate workflow for repository-connected Amplify apps.
    
    This is the most common case where the app is connected to GitHub via AWS Amplify.
    We cannot use create-deployment API, instead we:
    1. Deploy backend with ampx pipeline-deploy
    2. Let Amplify's automatic build handle the frontend
    3. Monitor the automatic build that gets triggered
    """
    
    return f"""name: Amplify Deploy (Repository-Connected)

on:
  push:
    branches: [{branch_name}]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.github/workflows/auto-fix-*.yml'

permissions:
  contents: write
  actions: read

concurrency:
  group: amplify-deploy-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      HUSKY: 0
      CI: 1
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 2
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      # Check for AWS credentials
      - name: Check AWS Credentials
        id: check-aws-creds
        run: |
          if [ -z "${{{{ secrets.AWS_ACCESS_KEY_ID }}}}" ] || [ -z "${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}" ]; then
            echo "❌ AWS credentials not configured!"
            echo ""
            echo "Please add AWS credentials to GitHub Secrets:"
            echo "1. Go to: https://github.com/${{{{ github.repository }}}}/settings/secrets/actions"
            echo "2. Add AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
            echo ""
            echo "credentials_configured=false" >> $GITHUB_OUTPUT
            exit 1
          else
            echo "✅ AWS credentials are configured"
            echo "credentials_configured=true" >> $GITHUB_OUTPUT
          fi
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.npm
            node_modules
            .next/cache
          key: ${{{{ runner.os }}}}-deps-${{{{ hashFiles('**/package-lock.json') }}}}
          restore-keys: |
            ${{{{ runner.os }}}}-deps-
      
      - name: Install dependencies
        run: |
          echo "📦 Installing dependencies..."
          npm ci --prefer-offline --no-audit || npm install
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{{{ secrets.AWS_ACCESS_KEY_ID }}}}
          aws-secret-access-key: ${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}
          aws-region: {aws_region}
      
      # Deploy backend only - frontend will auto-build
      - name: Deploy Amplify Backend
        id: backend-deploy
        run: |
          echo "🚀 Deploying backend for branch {branch_name}..."
          npx ampx pipeline-deploy --branch {branch_name} --app-id {app_id}
          
          # Generate outputs for local development
          echo "📝 Generating amplify_outputs.json..."
          npx ampx generate outputs --branch {branch_name} --app-id {app_id}
      
      # Commit outputs if changed
      - name: Commit amplify_outputs.json if changed
        run: |
          if [ -n "$(git status --porcelain amplify_outputs.json)" ]; then
            echo "📝 Committing updated amplify_outputs.json..."
            git config --global user.email "github-actions[bot]@users.noreply.github.com"
            git config --global user.name "github-actions[bot]"
            git add amplify_outputs.json
            git commit -m "Update amplify_outputs.json from backend deployment"
            git push
          else
            echo "✅ amplify_outputs.json is up to date"
          fi
      
      # Monitor the automatic Amplify build
      - name: Monitor Amplify Build
        id: monitor-build
        run: |
          echo "⏳ Waiting for Amplify automatic build to start..."
          
          # Get the commit SHA that will trigger the build
          COMMIT_SHA="${{{{ github.sha }}}}"
          echo "Monitoring builds for commit: $COMMIT_SHA"
          
          # Wait for build to appear (up to 2 minutes)
          MAX_WAIT=24
          WAIT_COUNT=0
          BUILD_FOUND=false
          JOB_ID=""
          
          while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
            echo "Checking for build (attempt $((WAIT_COUNT+1))/$MAX_WAIT)..."
            
            # List recent jobs
            JOBS_JSON=$(aws amplify list-jobs \
              --app-id {app_id} \
              --branch-name {branch_name} \
              --max-items 5 \
              2>/dev/null || echo "{{}}")
            
            if [ "$JOBS_JSON" != "{{}}" ]; then
              # Look for a job with our commit SHA
              JOB_ID=$(echo "$JOBS_JSON" | jq -r '.jobSummaries[] | select(.commitId == "'$COMMIT_SHA'") | .jobId' | head -1)
              
              if [ ! -z "$JOB_ID" ]; then
                echo "✅ Found Amplify build: $JOB_ID"
                BUILD_FOUND=true
                break
              fi
            fi
            
            WAIT_COUNT=$((WAIT_COUNT + 1))
            if [ $WAIT_COUNT -lt $MAX_WAIT ]; then
              sleep 5
            fi
          done
          
          if [ "$BUILD_FOUND" = "false" ]; then
            echo "⚠️ Amplify build not detected yet. It may still be starting..."
            echo "Check the Amplify Console: https://console.aws.amazon.com/amplify/apps/{app_id}/branches/{branch_name}"
            exit 0
          fi
          
          # Monitor the build progress
          echo "📊 Monitoring build $JOB_ID..."
          MAX_ATTEMPTS=60  # 30 minutes max
          ATTEMPT=0
          BUILD_STATUS="PENDING"
          
          while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
            # Get job status
            JOB_JSON=$(aws amplify get-job \
              --app-id {app_id} \
              --branch-name {branch_name} \
              --job-id "$JOB_ID" \
              2>/dev/null || echo "{{}}")
            
            if [ "$JOB_JSON" != "{{}}" ]; then
              BUILD_STATUS=$(echo "$JOB_JSON" | jq -r '.job.summary.status // "UNKNOWN"')
              echo "Build status: $BUILD_STATUS"
              
              if [ "$BUILD_STATUS" = "SUCCEED" ]; then
                echo "✅ Amplify build completed successfully!"
                
                # Get the app URL
                APP_URL=$(echo "$JOB_JSON" | jq -r '.job.steps[] | select(.stepName=="DEPLOY") | .artifacts.appArtifactUrl // ""')
                if [ ! -z "$APP_URL" ]; then
                  echo "🌐 App URL: $APP_URL"
                  echo "app_url=$APP_URL" >> $GITHUB_OUTPUT
                fi
                
                echo "build_status=success" >> $GITHUB_OUTPUT
                exit 0
                
              elif [ "$BUILD_STATUS" = "FAILED" ] || [ "$BUILD_STATUS" = "CANCELLED" ]; then
                echo "❌ Amplify build failed!"
                
                # Get error details
                echo "Error details:"
                echo "$JOB_JSON" | jq -r '.job.steps[] | select(.status=="FAILED") | "Step: \\(.stepName)\\nReason: \\(.reason // "Unknown")"'
                
                echo "build_status=failed" >> $GITHUB_OUTPUT
                exit 1
              fi
            fi
            
            ATTEMPT=$((ATTEMPT + 1))
            if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
              sleep 30
            fi
          done
          
          echo "⏱️ Build monitoring timeout. Check Amplify Console for status."
          echo "build_status=timeout" >> $GITHUB_OUTPUT
      
      # Summary
      - name: Deployment Summary
        if: always()
        run: |
          echo "## 🚀 Deployment Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          
          echo "### Configuration" >> $GITHUB_STEP_SUMMARY
          echo "- **App ID**: {app_id}" >> $GITHUB_STEP_SUMMARY
          echo "- **Branch**: {branch_name}" >> $GITHUB_STEP_SUMMARY
          echo "- **Region**: {aws_region}" >> $GITHUB_STEP_SUMMARY
          echo "- **Deployment Mode**: Repository-Connected" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          
          if [ "${{{{ steps.backend-deploy.outcome }}}}" = "success" ]; then
            echo "### ✅ Backend Deployment" >> $GITHUB_STEP_SUMMARY
            echo "Backend deployed successfully via pipeline-deploy" >> $GITHUB_STEP_SUMMARY
          else
            echo "### ❌ Backend Deployment Failed" >> $GITHUB_STEP_SUMMARY
            echo "Check the logs above for details" >> $GITHUB_STEP_SUMMARY
          fi
          echo "" >> $GITHUB_STEP_SUMMARY
          
          if [ "${{{{ steps.monitor-build.outputs.build_status }}}}" = "success" ]; then
            echo "### ✅ Frontend Build" >> $GITHUB_STEP_SUMMARY
            echo "Amplify automatic build completed successfully" >> $GITHUB_STEP_SUMMARY
            if [ ! -z "${{{{ steps.monitor-build.outputs.app_url }}}}" ]; then
              echo "**App URL**: ${{{{ steps.monitor-build.outputs.app_url }}}}" >> $GITHUB_STEP_SUMMARY
            fi
          elif [ "${{{{ steps.monitor-build.outputs.build_status }}}}" = "failed" ]; then
            echo "### ❌ Frontend Build Failed" >> $GITHUB_STEP_SUMMARY
            echo "Check the [Amplify Console](https://console.aws.amazon.com/amplify/apps/{app_id}/branches/{branch_name}) for details" >> $GITHUB_STEP_SUMMARY
          else
            echo "### ⏳ Frontend Build" >> $GITHUB_STEP_SUMMARY
            echo "Build may still be in progress. Check the [Amplify Console](https://console.aws.amazon.com/amplify/apps/{app_id}/branches/{branch_name})" >> $GITHUB_STEP_SUMMARY
          fi
"""


def get_manual_deployment_workflow(app_id: str, branch_name: str, aws_region: str = 'eu-north-1') -> str:
    """
    Generate workflow for manual deployment Amplify apps.
    
    This is for apps NOT connected to a repository.
    We can use webhooks and create-deployment API.
    """
    
    return f"""name: Amplify Deploy (Manual)

on:
  push:
    branches: [{branch_name}]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.github/workflows/auto-fix-*.yml'

permissions:
  contents: write

concurrency:
  group: amplify-deploy-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      HUSKY: 0
      CI: 1
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      # Check for AWS credentials
      - name: Check AWS Credentials
        id: check-aws-creds
        run: |
          if [ -z "${{{{ secrets.AWS_ACCESS_KEY_ID }}}}" ] || [ -z "${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}" ]; then
            echo "❌ AWS credentials not configured!"
            echo "credentials_configured=false" >> $GITHUB_OUTPUT
            exit 1
          else
            echo "✅ AWS credentials are configured"
            echo "credentials_configured=true" >> $GITHUB_OUTPUT
          fi
      
      - name: Install dependencies
        run: npm ci --prefer-offline --no-audit || npm install
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{{{ secrets.AWS_ACCESS_KEY_ID }}}}
          aws-secret-access-key: ${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}
          aws-region: {aws_region}
      
      # Deploy backend
      - name: Deploy Backend
        id: backend-deploy
        run: |
          echo "🚀 Deploying backend..."
          npx ampx pipeline-deploy --branch {branch_name} --app-id {app_id}
          
          echo "📝 Generating outputs..."
          npx ampx generate outputs --branch {branch_name} --app-id {app_id}
      
      # Build the frontend
      - name: Build Frontend
        run: |
          echo "🔨 Building frontend..."
          npm run build
      
      # Create deployment bundle
      - name: Create Deployment Bundle
        id: create-bundle
        run: |
          echo "📦 Creating deployment bundle..."
          
          # Create a zip of the build output
          if [ -d ".next" ]; then
            # Next.js build
            zip -r deploy.zip .next public package.json package-lock.json amplify_outputs.json node_modules
          elif [ -d "build" ]; then
            # React/Vue build
            zip -r deploy.zip build amplify_outputs.json
          elif [ -d "dist" ]; then
            # Other frameworks
            zip -r deploy.zip dist amplify_outputs.json
          else
            echo "❌ No build output found"
            exit 1
          fi
          
          # Upload to S3
          DEPLOYMENT_BUCKET="amplify-{app_id}-{branch_name}-deployment"
          BUNDLE_KEY="deploy-${{{{ github.sha }}}}.zip"
          
          # Create bucket if it doesn't exist
          aws s3api create-bucket \
            --bucket "$DEPLOYMENT_BUCKET" \
            --region {aws_region} \
            --create-bucket-configuration LocationConstraint={aws_region} \
            2>/dev/null || true
          
          # Upload bundle
          aws s3 cp deploy.zip "s3://$DEPLOYMENT_BUCKET/$BUNDLE_KEY"
          
          echo "bundle_s3_url=s3://$DEPLOYMENT_BUCKET/$BUNDLE_KEY" >> $GITHUB_OUTPUT
      
      # Create deployment
      - name: Create Amplify Deployment
        id: create-deployment
        run: |
          echo "🚀 Creating Amplify deployment..."
          
          # Create deployment
          DEPLOYMENT_JSON=$(aws amplify create-deployment \
            --app-id {app_id} \
            --branch-name {branch_name} \
            --region {aws_region})
          
          JOB_ID=$(echo "$DEPLOYMENT_JSON" | jq -r '.jobId')
          UPLOAD_URL=$(echo "$DEPLOYMENT_JSON" | jq -r '.zipUploadUrl')
          
          echo "job_id=$JOB_ID" >> $GITHUB_OUTPUT
          
          # Upload the bundle
          curl -T deploy.zip "$UPLOAD_URL"
          
          # Start deployment
          aws amplify start-deployment \
            --app-id {app_id} \
            --branch-name {branch_name} \
            --job-id "$JOB_ID" \
            --region {aws_region}
      
      # Monitor deployment
      - name: Monitor Deployment
        run: |
          echo "📊 Monitoring deployment..."
          
          JOB_ID="${{{{ steps.create-deployment.outputs.job_id }}}}"
          MAX_ATTEMPTS=60
          ATTEMPT=0
          
          while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
            JOB_JSON=$(aws amplify get-job \
              --app-id {app_id} \
              --branch-name {branch_name} \
              --job-id "$JOB_ID" \
              --region {aws_region})
            
            STATUS=$(echo "$JOB_JSON" | jq -r '.job.summary.status')
            echo "Status: $STATUS"
            
            if [ "$STATUS" = "SUCCEED" ]; then
              echo "✅ Deployment successful!"
              exit 0
            elif [ "$STATUS" = "FAILED" ]; then
              echo "❌ Deployment failed!"
              echo "$JOB_JSON" | jq '.job.steps[] | select(.status=="FAILED")'
              exit 1
            fi
            
            ATTEMPT=$((ATTEMPT + 1))
            sleep 30
          done
          
          echo "⏱️ Deployment timeout"
          exit 1
      
      - name: Summary
        if: always()
        run: |
          echo "## Deployment Summary" >> $GITHUB_STEP_SUMMARY
          echo "- **Mode**: Manual Deployment" >> $GITHUB_STEP_SUMMARY
          echo "- **App ID**: {app_id}" >> $GITHUB_STEP_SUMMARY
          echo "- **Branch**: {branch_name}" >> $GITHUB_STEP_SUMMARY
          
          if [ "${{{{ steps.create-deployment.outputs.job_id }}}}" != "" ]; then
            echo "- **Job ID**: ${{{{ steps.create-deployment.outputs.job_id }}}}" >> $GITHUB_STEP_SUMMARY
          fi
"""


def get_workflow_template(app_id: str, branch_name: str, aws_region: str = 'eu-north-1', deployment_mode: str = 'auto') -> str:
    """
    Get the appropriate workflow template based on deployment mode.
    
    Args:
        app_id: Amplify app ID
        branch_name: Git branch name
        aws_region: AWS region
        deployment_mode: 'repository', 'manual', or 'auto' (auto-detect)
    
    Returns:
        Appropriate workflow template as a string
    """
    
    if deployment_mode == 'repository':
        return get_repository_connected_workflow(app_id, branch_name, aws_region)
    elif deployment_mode == 'manual':
        return get_manual_deployment_workflow(app_id, branch_name, aws_region)
    else:
        # Default to repository-connected (most common case)
        # The server should detect and override this if needed
        return get_repository_connected_workflow(app_id, branch_name, aws_region)