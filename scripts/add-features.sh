#!/bin/bash

# Add-Features Script for Amplify Pipeline MCP
# Usage: ./add-features.sh [feature1] [feature2] ...
# Available features: test, notifications, performance, security, all

set -e

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
WORKFLOW_DIR="$REPO_ROOT/.github/workflows"
SCRIPTS_DIR="$REPO_ROOT/scripts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Amplify Pipeline Feature Installer"
echo "======================================"

# Function to add test runner
add_test_runner() {
    echo -e "${YELLOW}Adding test runner integration...${NC}"
    
    # Check if test script exists in package.json
    if ! grep -q '"test"' "$REPO_ROOT/package.json"; then
        echo "Adding test script to package.json..."
        # Add basic test script
        npm pkg set scripts.test="jest --passWithNoTests"
    fi
    
    # Add test job to workflow
    cat >> "$WORKFLOW_DIR/amplify-pipeline-test.yml" << 'EOF'
name: Test Runner

on:
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage
      - uses: actions/upload-artifact@v3
        with:
          name: coverage
          path: coverage/
EOF
    
    echo -e "${GREEN}✅ Test runner added!${NC}"
}

# Function to add notifications
add_notifications() {
    echo -e "${YELLOW}Adding notification system...${NC}"
    
    # Create notifications config
    cat > "$SCRIPTS_DIR/notify.js" << 'EOF'
#!/usr/bin/env node

const https = require('https');

async function sendNotification(webhook, message) {
    if (!webhook) return;
    
    const data = JSON.stringify({
        text: message,
        username: 'Amplify Pipeline',
        icon_emoji: ':rocket:'
    });
    
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': data.length
        }
    };
    
    return new Promise((resolve) => {
        const req = https.request(webhook, options, resolve);
        req.write(data);
        req.end();
    });
}

const status = process.env.DEPLOY_STATUS || 'unknown';
const branch = process.env.GITHUB_REF_NAME || 'unknown';
const webhook = process.env.SLACK_WEBHOOK_URL;

const message = status === 'success' 
    ? `✅ Deployment successful on ${branch}`
    : `❌ Deployment failed on ${branch}`;

sendNotification(webhook, message);
EOF
    
    chmod +x "$SCRIPTS_DIR/notify.js"
    
    echo -e "${GREEN}✅ Notification system added!${NC}"
    echo "   Add SLACK_WEBHOOK_URL to GitHub Secrets to enable"
}

# Function to add performance monitoring
add_performance() {
    echo -e "${YELLOW}Adding performance monitoring...${NC}"
    
    # Create bundle size check script
    cat > "$SCRIPTS_DIR/check-bundle-size.sh" << 'EOF'
#!/bin/bash

MAX_SIZE_MB=10
BUILD_DIR=".next"

if [ -d "$BUILD_DIR" ]; then
    SIZE=$(du -sm "$BUILD_DIR" | cut -f1)
    echo "Bundle size: ${SIZE}MB (limit: ${MAX_SIZE_MB}MB)"
    
    if [ $SIZE -gt $MAX_SIZE_MB ]; then
        echo "❌ Bundle size exceeds limit!"
        exit 1
    else
        echo "✅ Bundle size OK"
    fi
else
    echo "Build directory not found"
fi
EOF
    
    chmod +x "$SCRIPTS_DIR/check-bundle-size.sh"
    
    # Add to package.json
    npm pkg set scripts.check:size="./scripts/check-bundle-size.sh"
    
    echo -e "${GREEN}✅ Performance monitoring added!${NC}"
}

# Function to add security scanning
add_security() {
    echo -e "${YELLOW}Adding security scanning...${NC}"
    
    # Create security check workflow
    cat > "$WORKFLOW_DIR/security.yml" << 'EOF'
name: Security Scan

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run npm audit
        run: npm audit --audit-level=high
        continue-on-error: true
      
      - name: Run git-secrets
        run: |
          git clone https://github.com/awslabs/git-secrets.git
          cd git-secrets && make install
          cd ..
          git secrets --install
          git secrets --register-aws
          git secrets --scan
EOF
    
    echo -e "${GREEN}✅ Security scanning added!${NC}"
}

# Function to add all features
add_all() {
    add_test_runner
    add_notifications
    add_performance
    add_security
}

# Main logic
if [ $# -eq 0 ]; then
    echo "Usage: $0 [feature1] [feature2] ..."
    echo ""
    echo "Available features:"
    echo "  test          - Add test runner with coverage"
    echo "  notifications - Add Slack/Discord notifications"
    echo "  performance   - Add bundle size and performance checks"
    echo "  security      - Add security scanning"
    echo "  all           - Add all features"
    exit 1
fi

# Create directories if they don't exist
mkdir -p "$WORKFLOW_DIR"
mkdir -p "$SCRIPTS_DIR"

# Process arguments
for feature in "$@"; do
    case $feature in
        test)
            add_test_runner
            ;;
        notifications)
            add_notifications
            ;;
        performance)
            add_performance
            ;;
        security)
            add_security
            ;;
        all)
            add_all
            ;;
        *)
            echo -e "${RED}Unknown feature: $feature${NC}"
            ;;
    esac
done

echo ""
echo -e "${GREEN}🎉 Features added successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Review the generated files"
echo "2. Commit the changes"
echo "3. Add necessary secrets to GitHub"
echo "4. Push to trigger the pipeline"