# AWS Amplify Pipeline MCP Server

## 🎯 Smart Deployment Mode Detection

This MCP server **automatically detects** whether your Amplify app is:
- **Repository-Connected** (most common) - App connected to GitHub via AWS Amplify
- **Manual Deployment** (rare) - App not connected to any repository

### Repository-Connected Apps (95% of cases)
✅ **Automatic detection and configuration**
✅ **No webhooks or manual triggers needed**
✅ **Optimized for Git-based deployments**
✅ **Monitors automatic Amplify builds**

### Manual Deployment Apps (5% of cases)
✅ **Uses webhooks and create-deployment API**
✅ **Full control over deployment timing**
✅ **Suitable for apps without Git connection**

A Model Context Protocol (MCP) server that automates the setup of custom CI/CD pipelines for AWS Amplify Gen 2 applications with intelligent deployment mode detection.

> 📚 **[Complete Usage Guide](./COMPLETE_USAGE_GUIDE.md)** - Comprehensive guide for all features
> 🚀 **[Feature Roadmap](./FEATURE_ROADMAP.md)** - Upcoming features and enhancements
> 🤖 **[Auto-Fix Documentation](./AUTO_FIX_FEATURES.md)** - Deep dive into auto-fix system

## Overview

This MCP server intelligently detects your Amplify app's deployment mode and configures the optimal pipeline setup. With just one command - `pipeline-deploy` - everything is configured automatically based on whether your app is repository-connected or uses manual deployment.

## Features

### Core Capabilities
- 🔍 **Automatic Deployment Mode Detection**: Intelligently detects repository-connected vs manual apps
- 🎯 **Dual Workflow Templates**: Generates appropriate GitHub Actions based on deployment mode
- 🚀 **Smart Pipeline Setup**: Configures optimal CI/CD for your specific app configuration
- 📦 **Framework Detection**: Automatically detects Next.js, React, Vue, Angular, etc.
- 🔧 **Platform Configuration**: Sets correct platform (WEB_COMPUTE for SSR, WEB for SPA)

### Repository-Connected Features
- ✅ **No Manual Triggers**: Leverages Amplify's automatic builds
- 📊 **Build Monitoring**: Tracks automatic builds triggered by Git pushes
- 🔄 **Simplified Workflow**: Backend deploy → Git push → Auto frontend build
- ⚡ **Faster Deployments**: Optimized for the common case

### Manual Deployment Features  
- 🔗 **Webhook Management**: Creates webhooks for manual triggering
- 🎮 **Full Control**: Complete control over deployment timing
- 📦 **Bundle Creation**: Packages and deploys build artifacts
- 🛑 **Auto-Build Disable**: Turns off automatic builds for manual control

### Error Handling & Recovery
- 🤖 **Auto-Fix System**: Automatically fixes common deployment issues
- 🔍 **Error Detection**: Identifies wrong deployment mode usage
- 📝 **Smart Suggestions**: Provides actionable fixes for failures
- 🔄 **Retry Logic**: Automatic retries with fixes applied

## The New Workflow

### Step 1: Manual Setup (One Time)
1. Create your Amplify app in AWS Console
2. Connect your GitHub repository using the AWS Amplify GitHub App (for repository-connected mode)
3. This establishes the secure connection between Amplify and GitHub

### Step 2: Automated Pipeline Setup
From your repository directory, just say:
- **"pipeline deploy"** or
- **"set up pipeline"** or  
- **"p-deploy"**

That's it! The MCP server automatically detects your deployment mode and configures everything accordingly.

## What Happens Automatically

When you run `pipeline-deploy` with your app ID, the server:
- ✅ **Detects deployment mode** (repository-connected or manual)
- ✅ **Detects framework** (Next.js, React, Vue, etc.)
- ✅ **Configures appropriate workflow** based on mode
- ✅ Auto-detects your current Git branch
- ✅ For repository-connected: Ensures auto-build is enabled
- ✅ For manual: Disables auto-build and creates webhooks
- ✅ Generates optimal GitHub Actions workflow
- ✅ Creates auto-fix scripts for error recovery
- ✅ Sets up proper `amplify.yml` with Node.js 20

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **AWS Amplify App** created in AWS Console
3. **GitHub Repository** (connected for repository mode)
4. **Python 3.9+** installed
5. **Node.js 20+** for Amplify Gen 2
6. **MCP-compatible client** (like Claude Code)

## Quick Start

### 1. Install Dependencies
```bash
pip install mcp pyyaml
```

### 2. Add to Claude Code

```bash
# Using the shell script (recommended)
claude mcp add amplify-pipeline /Users/kjetilge/mcp-servers/amplify-pipeline-mcp/run_server.sh -s local

# Or using Python directly
claude mcp add amplify-pipeline "python /Users/kjetilge/mcp-servers/amplify-pipeline-mcp/server.py" -s local
```

### 3. Configure Your App

```bash
# The tool will auto-detect your deployment mode and configure accordingly
pipeline-deploy --app-id YOUR_APP_ID

# Example output:
# 🔍 Detecting deployment mode...
# ✅ Repository-connected app detected
# 📦 Framework: Next.js SSR (WEB_COMPUTE)
# 🌿 Branch: main
# 🚀 Setting up repository-connected pipeline...
```

## What Gets Created

### For Repository-Connected Apps (Most Common)
1. **Optimized GitHub Actions Workflow** - Deploys backend, monitors automatic frontend build
2. **amplify.yml** - Build configuration with Node.js 20
3. **Auto-Fix Scripts** - Handles common errors
4. **Build Monitoring** - Tracks automatic Amplify builds

### For Manual Deployment Apps (Rare)
1. **Manual Deployment Workflow** - Full control over deployments
2. **Webhook Configuration** - For triggering deployments
3. **Build Bundle Creation** - Packages artifacts for deployment
4. **Deployment Monitoring** - Tracks manual deployment status

## Common Issues & Solutions

### "Operation not supported" Error
**Problem**: Using manual deployment on a repository-connected app
**Solution**: The MCP server now automatically detects this and uses the correct workflow

### Missing amplify_outputs.json
**Problem**: Frontend can't find backend configuration
**Solution**: Automatically generated during backend deployment

### Package-lock.json Out of Sync
**Problem**: Dependencies mismatch between package.json and lock file
**Solution**: Automatically detected and fixed before deployment

## Architecture

### Repository-Connected Apps (Automatic Detection)
```
┌─────────────────┐
│  GitHub Push    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │
│   Workflow      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Backend Deploy  │
│ (pipeline-deploy)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Git Push with  │
│ amplify_outputs │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Amplify Auto    │
│ Build (Triggered│
│ by Git Push)    │
└─────────────────┘
```

### Manual Deployment Apps (Automatic Detection)
```
┌─────────────────┐
│  GitHub Push    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Backend Deploy  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create Bundle   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Manual Deploy   │
│ (create-deploy) │
└─────────────────┘
```

## Required GitHub Setup

After running `pipeline-deploy`, you need to:

1. **Add GitHub Secrets**:
   - `AWS_ACCESS_KEY_ID` - AWS access key for deployments
   - `AWS_SECRET_ACCESS_KEY` - AWS secret key for deployments

2. **Ensure Repository Permissions**:
   - GitHub Actions needs write permissions (added automatically to workflow)
   - Verify `amplify_outputs.json` is NOT in `.gitignore`

3. **Commit and Push**:
```bash
git add -A
git commit -m "Add custom pipeline configuration"
git push
```

## Auto-Fix Features

### What Gets Fixed Automatically

| Issue Type | Auto-Fix Action | When Applied |
|------------|----------------|---------------|
| Wrong deployment mode | Use correct workflow | Detection phase |
| Linting errors | ESLint --fix | Before deployment |
| Formatting | Prettier --write | Before deployment |
| TypeScript errors | Add missing types/imports | On failure |
| Security vulnerabilities | npm audit fix | On failure |
| Missing dependencies | npm install | On failure |
| Missing amplify_outputs.json | Generate from app ID | On failure |
| Package-lock sync | npm install | Before deployment |

## Usage Examples

### With Claude Code (Natural Language)

```
"Set up pipeline for my amplify app"
"Why is my build failing?"
"Is my app repository-connected?"
"Fix deployment errors"
```

### Direct Command

```
"pipeline deploy d1234abcd5678"
```

The app ID can be found in your Amplify Console URL:
- Go to AWS Amplify Console
- Click on your app
- The URL will be: `.../apps/d1234abcd5678/...`
- Copy the ID: `d1234abcd5678`

## Benefits

- **Intelligent Detection**: Automatically uses the right deployment strategy
- **Zero Configuration**: Works out of the box with auto-detection
- **Error Prevention**: Prevents "Operation not supported" errors
- **Full Control**: Complete control over build and deployment process
- **Custom Steps**: Add testing, linting, security scans, etc.
- **Integration**: Works with existing CI/CD systems
- **Auto-Fix**: Automatically resolves common deployment errors
- **Time Saving**: No manual fixing of deployment mode mismatches

## Documentation

- 📚 **[Complete Usage Guide](./COMPLETE_USAGE_GUIDE.md)** - Step-by-step instructions for all features
- 🤖 **[Auto-Fix Features](./AUTO_FIX_FEATURES.md)** - How the self-healing system works
- 🚀 **[Feature Roadmap](./FEATURE_ROADMAP.md)** - What's coming next
- 💡 **[Examples](./examples/)** - Sample configurations and use cases

## Support

### With Claude Code
Simply ask:
- "Help with pipeline setup"
- "Debug my failing build"  
- "What deployment mode is my app using?"
- "Fix repository connection issues"

### Manual Support
- Check the [Complete Usage Guide](./COMPLETE_USAGE_GUIDE.md)
- Review workflow logs in GitHub Actions
- Check AWS Amplify Console for frontend logs
- Ensure all prerequisites are met

## Development

### Project Structure

```
amplify-pipeline-mcp/
├── server.py                # Main MCP server implementation
├── deployment_detector.py   # Deployment mode detection logic
├── deployment_monitor.py    # Enhanced monitoring capabilities
├── workflow_templates.py    # Dual workflow templates
├── README.md               # User documentation
└── pyproject.toml          # Python package configuration
```

### Testing Checklist

- [ ] Test with repository-connected app
- [ ] Test with manual deployment app
- [ ] Test deployment mode detection
- [ ] Test framework detection
- [ ] Verify correct workflow generation
- [ ] Confirm error handling for wrong mode
- [ ] Check auto-fix capabilities

## License

MIT