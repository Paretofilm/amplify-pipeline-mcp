# 🤖 Auto-Fix Features in Amplify Pipeline MCP

## Overview

The Amplify Pipeline MCP server now automatically sets up comprehensive auto-fix capabilities every time it deploys a pipeline. This ensures that common deployment errors are automatically fixed without manual intervention.

## What Gets Set Up Automatically

When you run `pipeline_deploy`, the MCP server now creates:

### 1. Auto-Fix Script (`scripts/auto-fix.js`)
A comprehensive Node.js script that automatically fixes:
- ✅ ESLint issues
- ✅ Prettier formatting
- ✅ npm vulnerabilities
- ✅ TypeScript errors
- ✅ Missing imports
- ✅ Amplify configuration issues
- ✅ Missing `amplify_outputs.json`

### 2. Main Pipeline Workflow with Auto-Fix
The generated GitHub Actions workflow now includes:
- **Pre-deployment auto-fixes** that run before every deployment
- **Automatic linting fixes** with ESLint
- **Automatic formatting** with Prettier
- **Auto-commit of fixes** back to the repository
- **Smart skip logic** to avoid infinite loops

### 3. Auto-Fix on Failure Workflow
A separate workflow that:
- **Triggers automatically** when the main pipeline fails
- **Analyzes failure reason** and applies targeted fixes
- **Commits fixes** and retriggers the pipeline
- **Creates issues** for non-fixable problems

## How It Works

### During Normal Deployment

1. Push code to your branch
2. Pipeline starts and runs auto-fix steps:
   - Fixes linting issues
   - Fixes formatting
   - Commits any fixes with `[skip ci]` to avoid loops
3. Deploys backend with Amplify
4. Generates and commits `amplify_outputs.json`
5. Triggers frontend build

### When Build Fails

1. Main pipeline fails
2. Auto-Fix on Failure workflow triggers
3. Runs comprehensive auto-fix script
4. If fixes are found:
   - Commits them
   - New pipeline run starts automatically
5. If no fixes possible:
   - Workflow completes
   - Manual intervention needed

## Usage

Simply run the MCP server command as usual:

```bash
# The auto-fix system is set up automatically
pipeline_deploy app_id="your-app-id"
```

No additional configuration needed! The MCP server handles everything.

## Features Added to Each Pipeline

### Automatic Error Detection
- TypeScript compilation errors
- Linting violations
- Formatting inconsistencies
- Security vulnerabilities
- Missing dependencies
- Amplify configuration issues

### Smart Fix Application
- Only commits when changes are made
- Uses `[skip ci]` to prevent infinite loops
- Preserves git history with clear commit messages
- Non-destructive (only fixes, never deletes)

### Comprehensive Logging
- Clear emoji indicators (🔧 fixing, ✅ fixed, ❌ error)
- Detailed commit messages
- GitHub Actions annotations

## Customization

While the MCP server sets up sensible defaults, you can customize after setup:

### Modify Auto-Fix Script
Edit `scripts/auto-fix.js` to add custom fixes:

```javascript
// Add your custom fix
fixCustomIssue() {
  this.log('Fixing custom issue...', 'fix');
  // Your logic here
}
```

### Adjust Workflow Behavior
Edit `.github/workflows/amplify-pipeline-main.yml` to:
- Add more auto-fix steps
- Change when fixes are applied
- Modify commit messages

### Disable Specific Fixes
Comment out unwanted fix steps in the workflows or script.

## Benefits

1. **Zero Manual Intervention**: Most common errors fixed automatically
2. **Faster Deployment**: No waiting for developers to fix trivial issues
3. **Consistent Code Quality**: Formatting and linting always applied
4. **Reduced Failed Builds**: Many issues fixed before they cause failures
5. **Learning Tool**: Review auto-fix commits to learn from mistakes

## Requirements

The auto-fix system requires:
- GitHub Actions with `contents: write` permission (set automatically)
- Node.js 18+ (configured in workflows)
- Standard npm packages (ESLint, Prettier, TypeScript)

## Troubleshooting

### Auto-Fix Not Working

Check:
1. GitHub Actions permissions (needs write access)
2. Node modules are installed (`npm ci`)
3. Scripts directory exists
4. Workflow files are committed

### Too Many Auto-Fix Commits

The system uses `[skip ci]` to prevent loops. If you see many commits:
1. Check for syntax errors that auto-fix can't handle
2. Review the auto-fix script for issues
3. Temporarily disable with `[skip-fix]` in commit message

### Manual Override

To skip auto-fix for a specific commit:
```bash
git commit -m "Experimental changes [skip-fix]"
```

## Security

- Only runs on your repository code
- Uses GitHub Actions bot for commits
- No external dependencies beyond npm packages
- All fixes are logged and reviewable

## Future Enhancements

Planned improvements:
- [ ] AI-powered error analysis
- [ ] Custom fix rules via configuration
- [ ] Performance optimization caching
- [ ] Integration with more tools
- [ ] Slack/Discord notifications

## Support

The auto-fix system is maintained as part of the Amplify Pipeline MCP server. Report issues or suggest improvements to the MCP server repository.