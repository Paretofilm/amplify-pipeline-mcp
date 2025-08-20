# Quick Start Guide

## Prerequisites
✅ AWS Amplify app created in console  
✅ GitHub repository connected via Amplify GitHub App  
✅ Claude Code with MCP server installed  

## The One Command

From your repository directory:

```
pipeline deploy for app YOUR_APP_ID
```

### Finding Your App ID
1. Go to AWS Amplify Console
2. Click on your app
3. Look at the URL: `.../apps/d1234abcd5678/...`
4. Copy the ID: `d1234abcd5678`

## What Happens

1. **Uses** your provided app ID
2. **Auto-detects** your Git branch
3. **Disables** auto-build 
4. **Creates** webhook for frontend triggers
5. **Generates** GitHub Actions workflow
6. **Configures** build specifications

## Complete the Setup

1. **Add GitHub Secrets**:
   - Go to your repo Settings → Secrets
   - Add `AWS_ACCESS_KEY_ID`
   - Add `AWS_SECRET_ACCESS_KEY`

2. **Commit & Push**:
```bash
git add -A
git commit -m "Add pipeline"
git push
```

## Done! 🎉

Your custom pipeline is now active. Every push will:
- Deploy backend via GitHub Actions
- Trigger frontend build via webhook
- Deploy your complete app

## Common Commands

- `pipeline deploy` - Set up everything
- Check logs: `gh run list`
- Monitor builds: AWS Amplify Console

## Troubleshooting

**"App ID not found"**
→ Make sure you're in the right repository
→ Verify app is connected in Amplify Console

**"Workflow fails"**
→ Check GitHub secrets are set
→ Verify AWS credentials have permissions

**"Frontend build fails"**  
→ Remove `amplify_outputs*` from `.gitignore`
→ Check webhook URL in workflow