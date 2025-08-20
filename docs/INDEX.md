# 📚 Amplify Pipeline MCP Documentation Index

## Quick Links

### 🚀 Getting Started
- [README](../README.md) - Overview and quick start
- [Claude Code Guide](../CLAUDE_CODE_GUIDE.md) - Using with Claude Code
- [Basic Setup Example](../examples/basic-setup.md) - Step-by-step first setup

### 📖 Comprehensive Guides
- [Complete Usage Guide](../COMPLETE_USAGE_GUIDE.md) - All features explained
- [Auto-Fix Documentation](../AUTO_FIX_FEATURES.md) - Self-healing pipeline details
- [Feature Roadmap](../FEATURE_ROADMAP.md) - What's coming next

### 🎯 Feature Guides
- [Testing Integration](../examples/adding-tests.md) - Add test coverage
- [Notifications Setup](../examples/notifications-setup.md) - Slack, Discord, Email
- [Auto-Fix Scenarios](../examples/auto-fix-scenarios.md) - How auto-fix works

### 🛠️ Templates
- [Test Runner](../templates/test-runner.yml) - Testing workflow template
- [Notifications](../templates/notifications.yml) - Alert system templates
- [Performance Checks](../templates/performance-checks.yml) - Monitoring templates

### 🔧 Scripts
- [Add Features Script](../scripts/add-features.sh) - Quick feature installer
- [Auto-Fix Script](../scripts/auto-fix.js) - Error recovery system

---

## Documentation by User Type

### 👨‍💻 For Developers

**Start Here:**
1. [Basic Setup Example](../examples/basic-setup.md)
2. [Complete Usage Guide](../COMPLETE_USAGE_GUIDE.md)
3. [Auto-Fix Scenarios](../examples/auto-fix-scenarios.md)

**Key Features:**
- Auto-fix system for common errors
- Build caching for speed
- Test integration
- Performance monitoring

### 🤖 For Claude Code Users

**Start Here:**
1. [Claude Code Guide](../CLAUDE_CODE_GUIDE.md)
2. [README](../README.md) - Natural language commands

**Common Commands:**
- "Set up pipeline for my app"
- "Add testing to pipeline"
- "Why is my build failing?"
- "Make deployments faster"

### 🏗️ For DevOps Engineers

**Start Here:**
1. [Feature Roadmap](../FEATURE_ROADMAP.md)
2. [Templates Directory](../templates/)
3. [Complete Usage Guide](../COMPLETE_USAGE_GUIDE.md)

**Advanced Topics:**
- Multi-environment deployments
- Custom notification systems
- Performance optimization
- Security scanning

---

## Documentation by Task

### 📦 Initial Setup
1. [Basic Setup Example](../examples/basic-setup.md)
2. [README - Prerequisites](../README.md#prerequisites)
3. [Complete Usage Guide - Quick Start](../COMPLETE_USAGE_GUIDE.md#quick-start)

### 🧪 Adding Testing
1. [Testing Integration Guide](../examples/adding-tests.md)
2. [Test Runner Template](../templates/test-runner.yml)
3. [Complete Guide - Testing Section](../COMPLETE_USAGE_GUIDE.md#testing-integration)

### 🔔 Setting Up Notifications
1. [Notifications Setup Guide](../examples/notifications-setup.md)
2. [Notifications Templates](../templates/notifications.yml)
3. [Complete Guide - Notifications](../COMPLETE_USAGE_GUIDE.md#notifications)

### 🔧 Troubleshooting
1. [Auto-Fix Scenarios](../examples/auto-fix-scenarios.md)
2. [Complete Guide - Troubleshooting](../COMPLETE_USAGE_GUIDE.md#troubleshooting)
3. [Claude Code Guide - Debugging](../CLAUDE_CODE_GUIDE.md#troubleshooting-with-claude)

### ⚡ Performance Optimization
1. [Performance Templates](../templates/performance-checks.yml)
2. [Feature Roadmap - Performance](../FEATURE_ROADMAP.md#performance-monitoring)
3. [Complete Guide - Performance](../COMPLETE_USAGE_GUIDE.md#performance-features)

---

## Quick Reference

### File Structure
```
amplify-pipeline-mcp/
├── docs/
│   └── INDEX.md                         # This file
├── examples/
│   ├── basic-setup.md                   # Step-by-step setup
│   ├── adding-tests.md                  # Testing guide
│   ├── notifications-setup.md           # Alerts guide
│   └── auto-fix-scenarios.md            # Auto-fix examples
├── scripts/
│   ├── add-features.sh                  # Feature installer
│   └── auto-fix.js                      # Auto-generated
├── templates/
│   ├── test-runner.yml                  # Test workflow
│   ├── notifications.yml                # Alert templates
│   └── performance-checks.yml           # Monitoring
├── server.py                            # MCP server code
├── README.md                            # Main documentation
├── COMPLETE_USAGE_GUIDE.md              # Full guide
├── CLAUDE_CODE_GUIDE.md                 # Claude integration
├── AUTO_FIX_FEATURES.md                 # Auto-fix details
└── FEATURE_ROADMAP.md                   # Future plans
```

### Command Cheat Sheet

**With Claude Code:**
```
"Set up pipeline for d1234abcd5678"
"Add testing to my pipeline"
"Enable Slack notifications"
"Fix my failing build"
```

**Manual Commands:**
```bash
# Add features
./scripts/add-features.sh test
./scripts/add-features.sh notifications
./scripts/add-features.sh all

# Run auto-fix
node scripts/auto-fix.js

# Skip deployment
git commit -m "Changes [skip ci]"

# Skip auto-fix
git commit -m "Changes [skip-fix]"
```

### GitHub Secrets Required

| Secret | Required | Purpose |
|--------|----------|---------|
| `AWS_ACCESS_KEY_ID` | ✅ Yes | AWS deployment |
| `AWS_SECRET_ACCESS_KEY` | ✅ Yes | AWS deployment |
| `SLACK_WEBHOOK_URL` | ❌ No | Slack alerts |
| `DISCORD_WEBHOOK_URL` | ❌ No | Discord alerts |

---

## Getting Help

1. **With Claude Code**: Just ask! "Help with pipeline setup"
2. **Documentation**: Start with [Complete Usage Guide](../COMPLETE_USAGE_GUIDE.md)
3. **Examples**: Check the [examples directory](../examples/)
4. **GitHub Issues**: Check workflow logs in Actions tab

---

## Contributing

See [Feature Roadmap](../FEATURE_ROADMAP.md) for planned features and contribution guidelines.

Last updated: 2024