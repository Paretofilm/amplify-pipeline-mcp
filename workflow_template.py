"""
GitHub Actions Workflow Template for Amplify Pipeline
Uses standardized single IAM user approach
"""

def get_workflow_template(app_id: str, branch_name: str, aws_region: str = 'eu-north-1') -> str:
    """
    Generate GitHub Actions workflow with credential check and single IAM user approach
    """
    
    # Escape branch name for git operations
    escaped_branch = branch_name.replace('/', '\/')
    
    return f"""name: Amplify Backend Pipeline

on:
  push:
    branches: [{branch_name}]
    paths-ignore:
      - '**.md'
      - 'docs/**'

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
    
    steps:
      - uses: actions/checkout@v3
        with:
          token: ${{{{ secrets.GITHUB_TOKEN }}}}
          fetch-depth: 0
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
      
      # CHECK FOR AWS CREDENTIALS FIRST
      - name: Check AWS Credentials
        id: check-aws-creds
        run: |
          if [ -z "${{{{ secrets.AWS_ACCESS_KEY_ID }}}}" ] || [ -z "${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}" ]; then
            echo "::error::❌ AWS credentials not configured!"
            echo ""
            echo "::notice::📝 Please add AWS credentials to GitHub Secrets:"
            echo "::notice::1. Go to: https://github.com/${{{{ github.repository }}}}/settings/secrets/actions"
            echo "::notice::2. Click 'New repository secret'"
            echo "::notice::3. Add these two secrets:"
            echo "::notice::   • AWS_ACCESS_KEY_ID (from github-actions-amplify IAM user)"
            echo "::notice::   • AWS_SECRET_ACCESS_KEY (from github-actions-amplify IAM user)"
            echo ""
            echo "::notice::📚 Using standardized IAM user approach:"
            echo "::notice::   - Use the same 'github-actions-amplify' IAM user for all projects"
            echo "::notice::   - BUT you must add the secrets to EACH repository individually"
            echo "::notice::   - This is a GitHub limitation - repository secrets are not global"
            echo "::notice::   - If you need credentials: aws iam create-access-key --user-name github-actions-amplify"
            echo ""
            echo "::warning::⚠️ Skipping deployment until AWS credentials are configured"
            echo "credentials_configured=false" >> $GITHUB_OUTPUT
            exit 0
          else
            echo "✅ AWS credentials are configured"
            echo "credentials_configured=true" >> $GITHUB_OUTPUT
          fi
      
      # Only continue if credentials are configured
      - name: Cache dependencies
        if: steps.check-aws-creds.outputs.credentials_configured == 'true'
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
        if: steps.check-aws-creds.outputs.credentials_configured == 'true'
        run: npm ci --prefer-offline --no-audit || npm install
      
      - name: Auto-Fix Linting Issues
        if: steps.check-aws-creds.outputs.credentials_configured == 'true'
        id: lint-fix
        continue-on-error: true
        run: |
          npm run lint -- --fix || true
          if [ -n "$(git status --porcelain)" ]; then
            echo "has_fixes=true" >> $GITHUB_OUTPUT
          else
            echo "has_fixes=false" >> $GITHUB_OUTPUT
          fi
      
      - name: Configure AWS credentials
        if: steps.check-aws-creds.outputs.credentials_configured == 'true'
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{{{ secrets.AWS_ACCESS_KEY_ID }}}}
          aws-secret-access-key: ${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}
          aws-region: {aws_region}
      
      - name: Deploy Backend
        if: steps.check-aws-creds.outputs.credentials_configured == 'true'
        id: backend-deploy
        run: |
          echo "Deploying backend for branch {branch_name}..."
          npx ampx pipeline-deploy --branch {branch_name} --app-id {app_id}
        continue-on-error: true
      
      - name: Generate Outputs
        if: steps.check-aws-creds.outputs.credentials_configured == 'true' && steps.backend-deploy.outcome == 'success'
        run: |
          echo "Generating outputs..."
          npx ampx generate outputs --branch {branch_name} --app-id {app_id}
      
      - name: Trigger Frontend Deployment
        if: steps.check-aws-creds.outputs.credentials_configured == 'true' && steps.backend-deploy.outcome == 'success'
        id: trigger-frontend
        run: |
          echo "Triggering frontend deployment..."
          # Get webhook URL from stored config if available
          if [ -f .amplify-webhook-{app_id}-{branch_name}.json ]; then
            WEBHOOK_URL=$(jq -r '.webhookUrl' .amplify-webhook-{app_id}-{branch_name}.json)
            if [ ! -z "$WEBHOOK_URL" ]; then
              curl -X POST -d "{{}}" -H "Content-Type: application/json" "$WEBHOOK_URL"
              echo "webhook_triggered=true" >> $GITHUB_OUTPUT
            else
              echo "webhook_triggered=false" >> $GITHUB_OUTPUT
            fi
          else
            echo "webhook_triggered=false" >> $GITHUB_OUTPUT
          fi
      
      - name: Monitor Amplify Build
        if: steps.check-aws-creds.outputs.credentials_configured == 'true' && steps.backend-deploy.outcome == 'success' && steps.trigger-frontend.outputs.webhook_triggered == 'true'
        run: |
          echo "Waiting 2 minutes for Amplify build to start..."
          sleep 120
          
          # Monitor build for up to 15 minutes
          MAX_ATTEMPTS=30
          ATTEMPT=0
          BUILD_STATUS="PENDING"
          JOB_ID=""
          
          while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
            echo "Checking Amplify build status (attempt $((ATTEMPT+1))/$MAX_ATTEMPTS)..."
            
            # Get the latest job
            JOBS_JSON=$(aws amplify list-jobs --app-id {app_id} --branch-name {branch_name} --max-items 1 2>/dev/null || echo "{{}}")
            
            if [ "$JOBS_JSON" != "{{}}" ]; then
              JOB_ID=$(echo "$JOBS_JSON" | jq -r '.jobSummaries[0].jobId // ""')
              BUILD_STATUS=$(echo "$JOBS_JSON" | jq -r '.jobSummaries[0].status // "UNKNOWN"')
              
              echo "Build status: $BUILD_STATUS (Job ID: $JOB_ID)"
              
              if [ "$BUILD_STATUS" = "SUCCEED" ]; then
                echo "✅ Amplify build completed successfully!"
                break
              elif [ "$BUILD_STATUS" = "FAILED" ] || [ "$BUILD_STATUS" = "CANCELLED" ]; then
                echo "❌ Amplify build failed or was cancelled"
                
                # Get error logs
                echo "Fetching build logs..."
                aws amplify get-job --app-id {app_id} --branch-name {branch_name} --job-id "$JOB_ID" > job-details.json 2>/dev/null || true
                
                if [ -f job-details.json ]; then
                  echo "Build error details:"
                  jq -r '.job.steps[] | select(.status=="FAILED") | "Step: \\(.stepName)\\nStatus: \\(.status)\\nLog: \\(.logUrl)"' job-details.json || true
                  
                  # Check for common errors
                  ERROR_MSG=$(jq -r '.job.steps[] | select(.status=="FAILED") | .artifacts.logs // ""' job-details.json 2>/dev/null || echo "")
                  
                  echo "Attempting auto-fix based on error..."
                  
                  # Common fixes
                  if echo "$ERROR_MSG" | grep -q "npm install\\|dependencies"; then
                    echo "Detected dependency issue. Running npm install..."
                    npm install
                    git add package-lock.json
                    git diff --staged --quiet || {{
                      git config --local user.email "github-actions[bot]@users.noreply.github.com"
                      git config --local user.name "github-actions[bot]"
                      git commit -m "Auto-fix: Update package-lock.json for Amplify build"
                      git push
                      echo "::notice::📝 Fixed dependency issue and pushed changes. A new build will be triggered."
                    }}
                  elif echo "$ERROR_MSG" | grep -q "TypeScript\\|type error"; then
                    echo "Detected TypeScript issue. Running type check..."
                    npx tsc --noEmit || true
                    npm run lint -- --fix || true
                    git add -A
                    git diff --staged --quiet || {{
                      git config --local user.email "github-actions[bot]@users.noreply.github.com"
                      git config --local user.name "github-actions[bot]"
                      git commit -m "Auto-fix: Fix TypeScript and linting issues"
                      git push
                      echo "::notice::📝 Fixed TypeScript issues and pushed changes. A new build will be triggered."
                    }}
                  elif echo "$ERROR_MSG" | grep -q "amplify_outputs.json"; then
                    echo "Missing amplify_outputs.json. Generating..."
                    npx ampx generate outputs --branch {branch_name} --app-id {app_id}
                    git add amplify_outputs.json
                    git diff --staged --quiet || {{
                      git config --local user.email "github-actions[bot]@users.noreply.github.com"
                      git config --local user.name "github-actions[bot]"
                      git commit -m "Auto-fix: Add missing amplify_outputs.json"
                      git push
                      echo "::notice::📝 Added amplify_outputs.json and pushed changes. A new build will be triggered."
                    }}
                  else
                    echo "::error::Could not automatically fix the build error. Please check the Amplify Console for details."
                  fi
                fi
                
                exit 1
              elif [ "$BUILD_STATUS" = "RUNNING" ] || [ "$BUILD_STATUS" = "PROVISIONING" ]; then
                echo "Build is still in progress..."
              fi
            else
              echo "No build jobs found yet..."
            fi
            
            ATTEMPT=$((ATTEMPT + 1))
            if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
              echo "Waiting 30 seconds before next check..."
              sleep 30
            fi
          done
          
          if [ "$BUILD_STATUS" != "SUCCEED" ]; then
            echo "::warning::⚠️ Build monitoring timeout. Please check the Amplify Console for build status."
          fi
      
      - name: Backend Deploy Failed - Check Errors
        if: steps.check-aws-creds.outputs.credentials_configured == 'true' && steps.backend-deploy.outcome == 'failure'
        run: |
          echo "Backend deployment failed. Checking for common issues..."
          
          # Check if the app exists
          aws amplify get-app --app-id {app_id} 2>/dev/null || {{
            echo "::error::App {app_id} not found. Please ensure the app is created in Amplify Console."
            exit 1
          }}
          
          # Try to get more error details
          echo "Check the logs above for specific error messages"
          exit 1
      
      - name: Commit Auto-Fixes
        if: steps.check-aws-creds.outputs.credentials_configured == 'true' && steps.lint-fix.outputs.has_fixes == 'true'
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add -A
          git diff --staged --quiet || {{
            git commit -m "Auto-fix: Apply linting and formatting fixes [skip ci]"
            git push
          }}
      
      - name: Summary
        if: always()
        run: |
          echo "## Deployment Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          
          if [ "${{{{ steps.check-aws-creds.outputs.credentials_configured }}}}" != "true" ]; then
            echo "### ⚠️ AWS Credentials Not Configured" >> $GITHUB_STEP_SUMMARY
            echo "" >> $GITHUB_STEP_SUMMARY
            echo "Please add AWS credentials to GitHub Secrets to enable deployment:" >> $GITHUB_STEP_SUMMARY
            echo "1. Go to [GitHub Secrets](https://github.com/${{{{ github.repository }}}}/settings/secrets/actions)" >> $GITHUB_STEP_SUMMARY
            echo "2. Add \`AWS_ACCESS_KEY_ID\` and \`AWS_SECRET_ACCESS_KEY\`" >> $GITHUB_STEP_SUMMARY
            echo "" >> $GITHUB_STEP_SUMMARY
            echo "**Note:** We use a single IAM user (github-actions-amplify) for all projects to simplify management." >> $GITHUB_STEP_SUMMARY
            echo "" >> $GITHUB_STEP_SUMMARY
            echo "After adding secrets, push any change or re-run this workflow." >> $GITHUB_STEP_SUMMARY
          elif [ "${{{{ steps.backend-deploy.outcome }}}}" = "success" ]; then
            echo "✅ Deployment successful!" >> $GITHUB_STEP_SUMMARY
            echo "- Backend: Deployed" >> $GITHUB_STEP_SUMMARY
            echo "- Frontend: Webhook triggered" >> $GITHUB_STEP_SUMMARY
            echo "- App ID: {app_id}" >> $GITHUB_STEP_SUMMARY
            echo "- Branch: {branch_name}" >> $GITHUB_STEP_SUMMARY
          else
            echo "❌ Deployment failed" >> $GITHUB_STEP_SUMMARY
            echo "Check the logs for details." >> $GITHUB_STEP_SUMMARY
          fi
"""