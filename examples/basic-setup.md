# Example: Basic Pipeline Setup

## Scenario
You have a new Amplify Gen 2 app and want to set up a custom pipeline.

## Step 1: Get Your App ID

1. Go to AWS Amplify Console
2. Click on your app
3. Copy the app ID from the URL: `https://console.aws.amazon.com/amplify/apps/d1234abcd5678/...`
   - Your app ID: `d1234abcd5678`

## Step 2: Connect with GitHub

1. In Amplify Console, go to "Hosting" → "Repository"
2. Connect your GitHub repository
3. Install the AWS Amplify GitHub App when prompted

## Step 3: Run Pipeline Setup with Claude

```
You: "Set up pipeline for app d1234abcd5678"
```

Claude will:
1. ✅ Detect your current Git branch
2. ✅ Disable auto-build in Amplify
3. ✅ Create webhook for frontend triggers
4. ✅ Generate GitHub Actions workflow
5. ✅ Create auto-fix script
6. ✅ Set up error recovery workflow

## Step 4: Add GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add these secrets:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

## Step 5: Commit and Push

```bash
git add .
git commit -m "Add custom pipeline configuration"
git push
```

## Result

Your pipeline is now active! Every push will:
1. Auto-fix linting/formatting issues
2. Deploy backend with Amplify
3. Generate amplify_outputs.json
4. Trigger frontend build
5. Auto-recover from failures

## Monitoring

Check your pipeline:
- **GitHub**: Actions tab shows workflow runs
- **Amplify Console**: Shows frontend builds
- **CloudWatch**: Detailed backend logs

## Next Steps

Add more features:
```bash
./scripts/add-features.sh test           # Add testing
./scripts/add-features.sh notifications  # Add Slack alerts
```