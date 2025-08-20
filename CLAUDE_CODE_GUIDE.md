# 🤖 Claude Code Integration Guide

## How to Use This MCP Server with Claude Code

### Installation

1. **Add the MCP server to Claude Code:**
```bash
claude mcp add amplify-pipeline /path/to/amplify-pipeline-mcp/run_server.sh
```

2. **Verify installation:**
```bash
claude mcp list
```

You should see `amplify-pipeline` in the list.

---

## Natural Language Commands

Claude Code understands these conversational requests:

### Basic Setup
```
"Set up a pipeline for my Amplify app"
"Configure CI/CD for this project"
"I need a custom pipeline"
"Help me deploy my Amplify app"
```

### Feature Additions
```
"Add testing to my pipeline"
"I want Slack notifications for deployments"
"Set up performance monitoring"
"Add security scanning"
"Make my builds faster"
```

### Troubleshooting
```
"Why is my build failing?"
"Debug this deployment error"
"The pipeline is slow, help optimize it"
"Fix the TypeScript errors in CI"
```

### Status Checks
```
"Check pipeline status"
"Show recent deployments"
"Are there any failing builds?"
"What's the current deployment?"
```

---

## Common Workflows with Claude

### 1. Initial Setup

```
You: "I have an Amplify app that needs a custom pipeline"
Claude: "I'll help you set up a custom pipeline. What's your app ID from the Amplify Console?"
You: "di441fw7gu9yh"
Claude: [Sets up everything automatically]
```

### 2. Adding Features Progressively

```
You: "The pipeline is working but I want to add tests"
Claude: [Adds test integration]

You: "Great! Now add Slack notifications"
Claude: [Adds Slack integration and explains how to get webhook]

You: "Also check bundle sizes"
Claude: [Adds performance monitoring]
```

### 3. Debugging Failures

```
You: "My build is failing with an error"
Claude: [Checks logs, identifies issue, runs auto-fix]

You: "It's still failing"
Claude: [Analyzes deeper, suggests manual fixes, helps implement them]
```

### 4. Optimization Requests

```
You: "Make my deployments faster"
Claude: [Enables caching, parallelizes jobs, optimizes steps]

You: "Reduce the bundle size"
Claude: [Analyzes bundle, suggests code splitting, implements lazy loading]
```

---

## Claude's Capabilities

### What Claude Can Do Automatically

✅ **Setup & Configuration**
- Detect your app ID and branch
- Create all necessary workflows
- Set up auto-fix systems
- Configure webhooks

✅ **Feature Addition**
- Add testing, notifications, monitoring
- Configure security scanning
- Set up performance checks
- Enable advanced caching

✅ **Troubleshooting**
- Read and analyze error logs
- Run auto-fix procedures
- Suggest manual fixes
- Debug configuration issues

✅ **Optimization**
- Speed up builds
- Reduce bundle sizes
- Improve test performance
- Optimize workflows

### What Claude Needs From You

❌ **Cannot Access Without Permission**
- AWS Console (needs app ID from you)
- GitHub Secrets (you must add these)
- Slack/Discord webhooks (you provide)
- AWS credentials (you configure)

---

## Interactive Examples

### Example 1: Complete Setup Flow

```
You: "Help me set up a pipeline for my new app"

Claude: "I'll help you set up a custom pipeline for your Amplify app. 
        First, I need your app ID. You can find it in the AWS Amplify 
        Console URL."

You: "How do I find that?"

Claude: "1. Go to AWS Amplify Console
        2. Click on your app
        3. Look at the URL: .../apps/[APP_ID]/...
        4. Copy the ID part"

You: "Got it, it's d3fx7example123"

Claude: [Runs pipeline_deploy with the app ID]
        "Perfect! I've set up your pipeline with:
        ✅ Auto-fix system for errors
        ✅ Build caching for speed
        ✅ GitHub Actions workflow
        
        Now add these GitHub secrets:
        - AWS_ACCESS_KEY_ID
        - AWS_SECRET_ACCESS_KEY"

You: "Done! What next?"

Claude: "Just push your code! The pipeline will handle everything.
        Want me to add testing or notifications?"
```

### Example 2: Progressive Enhancement

```
You: "My pipeline works but I want more features"

Claude: "Great! Your pipeline already has the basics. 
        What would you like to add?
        - 🧪 Testing with coverage
        - 🔔 Notifications (Slack/Discord)
        - 📊 Performance monitoring
        - 🔐 Security scanning"

You: "Let's start with testing"

Claude: [Adds test integration]
        "Testing added! Your pipeline now:
        - Runs tests before deployment
        - Generates coverage reports
        - Blocks deployment if tests fail
        
        What's next?"

You: "Add Slack notifications"

Claude: "I'll add Slack notifications. First, you need a webhook:
        1. Go to api.slack.com/apps
        2. Create an app
        3. Enable Incoming Webhooks
        4. Get the webhook URL
        
        Do you have it?"

You: "Yes, here it is: https://hooks.slack.com/..."

Claude: "Perfect! Add this as SLACK_WEBHOOK_URL in GitHub Secrets,
        and I'll configure the notifications."
        [Updates workflow with notifications]
```

### Example 3: Troubleshooting

```
You: "My deployment is failing"

Claude: [Checks recent workflow runs]
        "I see the issue - TypeScript errors in your latest commit.
        The auto-fix system attempted to fix them but needs manual
        intervention. Here are the errors:
        
        1. Missing type for 'user' parameter
        2. Incorrect import path for utils
        
        Should I help you fix these?"

You: "Yes please"

Claude: [Fixes the TypeScript errors]
        "Fixed! The changes:
        1. Added proper typing for user parameter
        2. Corrected import path to use @ alias
        
        Push these changes to trigger a new deployment."
```

---

## Tips for Working with Claude

### 1. Be Specific When Needed
```
Good: "Add testing with 80% coverage requirement"
Better: "Add Jest testing with 80% coverage for components only"
```

### 2. Ask for Explanations
```
"Why did the auto-fix add that commit?"
"What does this workflow step do?"
"Explain the caching strategy"
```

### 3. Request Alternatives
```
"Is there a faster way to do this?"
"What are other notification options?"
"Show me different testing strategies"
```

### 4. Iterate Progressively
Start simple, add features as needed:
1. Basic pipeline
2. Add testing
3. Add notifications
4. Add performance monitoring

### 5. Use Claude for Learning
```
"Explain how GitHub Actions works"
"What's the difference between amplify.yml and workflow?"
"Why do we need webhooks?"
```

---

## Command Reference

### Pipeline Commands
| Natural Language | What It Does |
|-----------------|--------------|
| "Set up pipeline" | Creates complete pipeline with auto-fix |
| "Add testing" | Integrates test runner with coverage |
| "Enable notifications" | Sets up Slack/Discord alerts |
| "Add caching" | Optimizes build speed |
| "Fix my build" | Runs auto-fix and troubleshooting |

### Information Commands
| Natural Language | What It Does |
|-----------------|--------------|
| "Check status" | Shows pipeline status |
| "Show logs" | Displays recent build logs |
| "Explain this error" | Analyzes and explains errors |
| "What features are available?" | Lists all possible additions |

### Optimization Commands
| Natural Language | What It Does |
|-----------------|--------------|
| "Make it faster" | Optimizes build performance |
| "Reduce bundle size" | Adds size checking and optimization |
| "Improve caching" | Enhances cache strategy |
| "Parallelize builds" | Runs jobs concurrently |

---

## Troubleshooting with Claude

### Claude Says "Tool Not Available"

```
You: "Restart Claude Code"
Then: "claude mcp list" (verify amplify-pipeline is there)
```

### Claude Can't Find Your App

```
You: "Here's my app ID: d1234abcd5678"
Claude: [Uses the provided ID]
```

### Features Not Working

```
You: "The notifications aren't sending"
Claude: [Checks webhook configuration, secrets, and logs]
```

---

## Best Practices

1. **Start Simple**: Basic pipeline first, add features gradually
2. **Trust Auto-Fix**: Let it handle routine issues
3. **Review Changes**: Check what Claude creates
4. **Ask Questions**: Claude can explain everything
5. **Iterate Fast**: Make small changes, deploy often

---

## Getting Help

If something isn't working:

1. **Ask Claude directly**: "Help with [specific issue]"
2. **Check the guide**: "Show me the usage guide"
3. **Review examples**: "Show me an example of [feature]"
4. **Debug with Claude**: "Why is this failing?"

Remember: Claude Code with this MCP server is designed to make pipeline management conversational and intuitive. Just describe what you want in plain English!