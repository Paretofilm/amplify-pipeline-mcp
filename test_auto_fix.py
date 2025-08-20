#!/usr/bin/env python3
"""Test that auto-fix components are created correctly"""

import tempfile
import shutil
from pathlib import Path
import sys
import os
import asyncio

# Add parent directory to path to import server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import AmplifyPipelineManager

async def test_auto_fix_creation():
    """Test that auto-fix scripts and workflows are created"""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing in temporary directory: {temp_dir}")
        
        manager = AmplifyPipelineManager()
        
        # Test 1: Create auto-fix script
        print("\n✓ Testing auto-fix script creation...")
        result = await manager.create_auto_fix_script(temp_dir)
        
        assert result['success'], "Failed to create auto-fix script"
        script_path = Path(temp_dir) / 'scripts' / 'auto-fix.js'
        assert script_path.exists(), "Auto-fix script file not created"
        
        # Check script content
        content = script_path.read_text()
        assert 'AutoFixer' in content, "AutoFixer class not in script"
        assert 'fixLinting' in content, "Linting fix not in script"
        assert 'fixAmplifyIssues' in content, "Amplify fixes not in script"
        print("  ✅ Auto-fix script created successfully")
        
        # Test 2: Create auto-fix on failure workflow
        print("\n✓ Testing auto-fix on failure workflow...")
        result = await manager.create_auto_fix_on_failure_workflow(temp_dir)
        
        assert result['success'], "Failed to create auto-fix workflow"
        workflow_path = Path(temp_dir) / '.github' / 'workflows' / 'auto-fix-on-failure.yml'
        assert workflow_path.exists(), "Auto-fix workflow file not created"
        
        # Check workflow content
        content = workflow_path.read_text()
        assert 'Auto-Fix on Failure' in content, "Workflow name not correct"
        assert 'workflow_run' in content, "Workflow trigger not correct"
        assert 'scripts/auto-fix.js' in content, "Script reference not in workflow"
        print("  ✅ Auto-fix on failure workflow created successfully")
        
        # Test 3: Verify main workflow has auto-fix steps
        print("\n✓ Testing main workflow with auto-fix...")
        # Create a mock webhook file for testing
        webhook_file = Path(temp_dir) / '.amplify-webhook-test123-main.json'
        webhook_file.write_text('{"webhookUrl": "https://test.webhook.url"}')
        
        result = await manager.setup_github_workflow('test123', 'main', temp_dir)
        
        workflow_path = Path(temp_dir) / '.github' / 'workflows' / 'amplify-pipeline-main.yml'
        assert workflow_path.exists(), "Main workflow file not created"
        
        content = workflow_path.read_text()
        assert 'Auto-Fix Linting Issues' in content, "Linting auto-fix not in workflow"
        assert 'Auto-Fix Prettier Formatting' in content, "Prettier auto-fix not in workflow"
        assert 'permissions:\n  contents: write' in content, "Write permissions not set"
        print("  ✅ Main workflow includes auto-fix steps")
        
        print("\n🎉 All auto-fix components created successfully!")
        return True

if __name__ == "__main__":
    success = asyncio.run(test_auto_fix_creation())
    sys.exit(0 if success else 1)