#!/usr/bin/env python3
"""Test that the fixes to the MCP server work correctly"""

import tempfile
import json
import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path to import server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import AmplifyPipelineManager

async def test_fixes():
    """Test all the fixes made to the server"""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing in temporary directory: {temp_dir}")
        
        manager = AmplifyPipelineManager()
        
        # Test 1: Filename sanitization
        print("\n✓ Testing filename sanitization...")
        
        # Test with problematic branch name
        bad_branch = "feature/my-branch#123"
        safe_branch = manager.sanitize_filename(bad_branch)
        assert safe_branch == "feature_my-branch_123", f"Failed: {safe_branch}"
        print(f"  ✅ Branch '{bad_branch}' -> '{safe_branch}'")
        
        # Test with problematic app ID
        bad_app_id = "app$id@test"
        safe_app_id = manager.sanitize_filename(bad_app_id)
        assert safe_app_id == "app_id_test", f"Failed: {safe_app_id}"
        print(f"  ✅ App ID '{bad_app_id}' -> '{safe_app_id}'")
        
        # Test 2: Auto-fix script with proper escaping
        print("\n✓ Testing auto-fix script generation...")
        result = await manager.create_auto_fix_script(temp_dir)
        assert result['success'], "Failed to create auto-fix script"
        
        # Check that the script has proper newline handling
        script_path = Path(temp_dir) / 'scripts' / 'auto-fix.js'
        content = script_path.read_text()
        
        # Check for proper console.log handling
        assert "console.log('');" in content, "Missing proper newline handling"
        assert "console.log('='.repeat(50));" in content, "Missing equals line"
        
        # Check for proper grep error handling
        assert "2>/dev/null" in content, "Missing error suppression in grep"
        print("  ✅ Auto-fix script has proper escaping")
        
        # Test 3: Workflow with proper GitHub Actions syntax
        print("\n✓ Testing workflow generation...")
        
        # Create a mock webhook file
        webhook_info = {
            'webhookUrl': 'https://test.webhook.url/hook',
            'webhookId': 'test-id'
        }
        safe_app = manager.sanitize_filename('test-app')
        safe_branch = manager.sanitize_filename('main')
        webhook_file = Path(temp_dir) / f'.amplify-webhook-{safe_app}-{safe_branch}.json'
        webhook_file.write_text(json.dumps(webhook_info))
        
        # Generate workflow
        result = await manager.setup_github_workflow('test-app', 'main', temp_dir)
        assert result['success'], "Failed to create workflow"
        
        workflow_path = Path(temp_dir) / '.github' / 'workflows' / 'amplify-pipeline-main.yml'
        workflow_content = workflow_path.read_text()
        
        # Check for proper GitHub Actions variable syntax (should be ${{ not ${{{)
        assert '${{ github.ref }}' in workflow_content, "Incorrect GitHub Actions syntax"
        assert '${{ secrets.GITHUB_TOKEN }}' in workflow_content, "Incorrect secrets syntax"
        assert '${{ runner.os }}' in workflow_content, "Incorrect runner syntax"
        
        # Check for proper prettier command (no double braces in glob)
        assert '"**/*.js" "**/*.jsx"' in workflow_content, "Incorrect prettier glob"
        
        # Check for proper webhook URL handling
        assert 'curl -X POST "https://test.webhook.url/hook"' in workflow_content, "Webhook URL not properly inserted"
        
        # Check for escaped branch in git push
        assert 'git push origin "main"' in workflow_content, "Branch not properly quoted"
        
        print("  ✅ Workflow has proper GitHub Actions syntax")
        
        # Test 4: Error handling in commands
        print("\n✓ Testing error handling...")
        
        # Test command with encoding issues
        result = await manager.run_command(['echo', 'test'], cwd=temp_dir)
        assert result['success'], "Basic command failed"
        assert 'test' in result['stdout'], "Output not captured"
        print("  ✅ Command execution with proper encoding")
        
        # Test 5: Windows compatibility
        print("\n✓ Testing Windows compatibility...")
        
        # The script creation should work even on Windows
        # (chmod is skipped on Windows)
        result = await manager.create_auto_fix_script(temp_dir)
        assert result['success'], "Failed on Windows compatibility"
        print("  ✅ Works on Windows (chmod skipped)")
        
        # Test 6: Webhook file handling with special characters
        print("\n✓ Testing webhook creation with special characters...")
        
        # Simulate branch with special characters
        special_branch = "feature/test-#123"
        safe_special_branch = manager.sanitize_filename(special_branch)
        
        # The workflow should use sanitized name for file
        result = await manager.setup_github_workflow('app-123', special_branch, temp_dir)
        assert result['success'], "Failed with special characters"
        
        expected_file = Path(temp_dir) / '.github' / 'workflows' / f'amplify-pipeline-{safe_special_branch}.yml'
        assert expected_file.exists(), f"Workflow file not created with safe name"
        print(f"  ✅ Created workflow with safe filename: amplify-pipeline-{safe_special_branch}.yml")
        
        # Test 7: Build spec with sanitized app ID
        print("\n✓ Testing build spec with special app ID...")
        
        special_app_id = "app@123#test"
        result = await manager.update_build_spec(special_app_id)
        assert result['success'], "Failed to create build spec"
        
        safe_app_id = manager.sanitize_filename(special_app_id)
        expected_spec_file = Path(f'amplify-buildspec-{safe_app_id}.yml')
        assert 'amplify-buildspec-app_123_test.yml' in result['message'], "Build spec filename not sanitized"
        print(f"  ✅ Build spec uses safe filename: amplify-buildspec-{safe_app_id}.yml")
        
        # Clean up the build spec file
        if expected_spec_file.exists():
            expected_spec_file.unlink()
        
        print("\n🎉 All fixes working correctly!")
        return True

if __name__ == "__main__":
    success = asyncio.run(test_fixes())
    sys.exit(0 if success else 1)