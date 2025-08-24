#!/usr/bin/env python3
"""
Deployment Mode Detection for AWS Amplify Apps

This module detects whether an Amplify app is configured for:
- Repository-connected deployment (most common)
- Manual deployment (rare)

It also detects framework and platform configuration.
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class DeploymentDetector:
    """Detects deployment mode and configuration for Amplify apps"""
    
    def __init__(self, aws_region: str = 'eu-north-1'):
        self.aws_region = aws_region
    
    async def run_command(self, cmd: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """Execute a shell command and return the result"""
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            stdout, stderr = await result.communicate()
            
            return {
                'success': result.returncode == 0,
                'stdout': stdout.decode('utf-8', errors='replace'),
                'stderr': stderr.decode('utf-8', errors='replace'),
                'returncode': result.returncode
            }
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def detect_deployment_mode(self, app_id: str, branch_name: str) -> Dict[str, Any]:
        """
        Detect if app uses repository-connected or manual deployment mode
        
        Returns:
            Dict with:
            - deployment_mode: 'repository' or 'manual'
            - repository_url: URL if repository-connected
            - auto_build: Whether auto-build is enabled
            - framework: Detected framework
            - platform: WEB or WEB_COMPUTE
        """
        logger.info(f"Detecting deployment mode for app {app_id} branch {branch_name}")
        
        # Get branch information
        cmd = [
            'aws', 'amplify', 'get-branch',
            '--app-id', app_id,
            '--branch-name', branch_name,
            '--region', self.aws_region
        ]
        
        result = await self.run_command(cmd)
        
        if not result['success']:
            # Branch doesn't exist or other error
            logger.warning(f"Could not get branch info: {result.get('stderr', '')}")
            
            # Try to get app info instead
            cmd = [
                'aws', 'amplify', 'get-app',
                '--app-id', app_id,
                '--region', self.aws_region
            ]
            
            app_result = await self.run_command(cmd)
            
            if not app_result['success']:
                return {
                    'success': False,
                    'error': 'Could not detect deployment mode - app or branch not found',
                    'deployment_mode': 'unknown'
                }
            
            try:
                app_data = json.loads(app_result['stdout'])
                app_info = app_data.get('app', {})
                
                # Check if repository is configured at app level
                repo_url = app_info.get('repository')
                
                return {
                    'success': True,
                    'deployment_mode': 'repository' if repo_url else 'manual',
                    'repository_url': repo_url,
                    'auto_build': False,  # Can't determine without branch
                    'framework': app_info.get('framework', 'Next.js - SSR'),
                    'platform': app_info.get('platform', 'WEB_COMPUTE'),
                    'branch_exists': False
                }
            except Exception as e:
                logger.error(f"Failed to parse app data: {e}")
                return {
                    'success': False,
                    'error': f'Failed to parse app data: {str(e)}',
                    'deployment_mode': 'unknown'
                }
        
        try:
            branch_data = json.loads(result['stdout'])
            branch_info = branch_data.get('branch', {})
            
            # Check for repository connection
            # If sourceRepository exists, it's repository-connected
            source_repo = branch_info.get('sourceRepository')
            
            # Get auto-build status
            auto_build = branch_info.get('enableAutoBuild', False)
            
            # Get framework (from branch or app level)
            framework = branch_info.get('framework', 'Next.js - SSR')
            
            # Get platform (WEB_COMPUTE for SSR, WEB for SPA)
            # This is typically at the app level, not branch
            platform = 'WEB_COMPUTE'  # Default for Next.js SSR
            
            # Try to get app-level info for platform
            cmd = [
                'aws', 'amplify', 'get-app',
                '--app-id', app_id,
                '--region', self.aws_region
            ]
            
            app_result = await self.run_command(cmd)
            if app_result['success']:
                try:
                    app_data = json.loads(app_result['stdout'])
                    app_info = app_data.get('app', {})
                    platform = app_info.get('platform', 'WEB_COMPUTE')
                    
                    # If no repo at branch level, check app level
                    if not source_repo:
                        source_repo = app_info.get('repository')
                    
                    # Get framework from app if not in branch
                    if not framework:
                        framework = app_info.get('framework', 'Next.js - SSR')
                except:
                    pass
            
            deployment_mode = 'repository' if source_repo else 'manual'
            
            result = {
                'success': True,
                'deployment_mode': deployment_mode,
                'repository_url': source_repo,
                'auto_build': auto_build,
                'framework': framework,
                'platform': platform,
                'branch_exists': True,
                'branch_info': {
                    'name': branch_info.get('branchName'),
                    'stage': branch_info.get('stage', 'PRODUCTION'),
                    'display_name': branch_info.get('displayName'),
                    'enable_basic_auth': branch_info.get('enableBasicAuth', False),
                    'enable_pull_request_preview': branch_info.get('enablePullRequestPreview', False)
                }
            }
            
            logger.info(f"Detected deployment mode: {deployment_mode}, framework: {framework}, platform: {platform}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse branch data: {e}")
            return {
                'success': False,
                'error': f'Failed to parse branch data: {str(e)}',
                'deployment_mode': 'unknown'
            }
    
    async def detect_framework_from_package_json(self, repo_path: str) -> Dict[str, Any]:
        """
        Detect framework from package.json
        
        Returns:
            Dict with:
            - framework: Detected framework name
            - version: Framework version
            - platform: Recommended platform (WEB or WEB_COMPUTE)
            - build_command: Suggested build command
        """
        package_json_path = Path(repo_path) / 'package.json'
        
        if not package_json_path.exists():
            return {
                'success': False,
                'error': 'No package.json found'
            }
        
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            dependencies = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
            scripts = package_data.get('scripts', {})
            
            # Detect framework based on dependencies
            framework = 'Unknown'
            version = 'Unknown'
            platform = 'WEB'
            build_command = 'npm run build'
            
            if 'next' in dependencies:
                framework = 'Next.js - SSR'
                version = dependencies['next']
                platform = 'WEB_COMPUTE'  # Next.js needs compute for SSR
                build_command = scripts.get('build', 'next build')
                
                # Check if it's static export
                next_config_path = Path(repo_path) / 'next.config.js'
                next_config_mjs_path = Path(repo_path) / 'next.config.mjs'
                
                config_path = next_config_path if next_config_path.exists() else (
                    next_config_mjs_path if next_config_mjs_path.exists() else None
                )
                
                if config_path:
                    with open(config_path, 'r') as f:
                        config_content = f.read()
                        if 'output.*:.*["\']export["\']' in config_content or "output: 'export'" in config_content:
                            framework = 'Next.js - Static'
                            platform = 'WEB'  # Static export doesn't need compute
                
            elif 'react' in dependencies and 'react-scripts' in dependencies:
                framework = 'React'
                version = dependencies['react']
                platform = 'WEB'
                build_command = scripts.get('build', 'react-scripts build')
                
            elif 'vue' in dependencies:
                framework = 'Vue'
                version = dependencies['vue']
                platform = 'WEB'
                build_command = scripts.get('build', 'vue-cli-service build')
                
            elif '@angular/core' in dependencies:
                framework = 'Angular'
                version = dependencies['@angular/core']
                platform = 'WEB'
                build_command = scripts.get('build', 'ng build')
                
            elif 'gatsby' in dependencies:
                framework = 'Gatsby'
                version = dependencies['gatsby']
                platform = 'WEB'
                build_command = scripts.get('build', 'gatsby build')
                
            elif 'nuxt' in dependencies or 'nuxt3' in dependencies:
                framework = 'Nuxt.js'
                version = dependencies.get('nuxt', dependencies.get('nuxt3', 'Unknown'))
                platform = 'WEB_COMPUTE'  # Nuxt needs compute for SSR
                build_command = scripts.get('build', 'nuxt build')
            
            # Check for Amplify dependencies
            has_amplify = '@aws-amplify/backend' in dependencies or 'aws-amplify' in dependencies
            
            return {
                'success': True,
                'framework': framework,
                'version': version,
                'platform': platform,
                'build_command': build_command,
                'has_amplify': has_amplify,
                'scripts': scripts
            }
            
        except Exception as e:
            logger.error(f"Failed to detect framework: {e}")
            return {
                'success': False,
                'error': f'Failed to detect framework: {str(e)}'
            }
    
    async def check_deployment_prerequisites(self, app_id: str, branch_name: str, repo_path: str) -> Dict[str, Any]:
        """
        Check all prerequisites for deployment
        
        Returns comprehensive status of:
        - Deployment mode
        - Framework detection
        - Branch configuration
        - Build settings
        - Required files
        """
        results = {
            'app_id': app_id,
            'branch_name': branch_name,
            'checks': {}
        }
        
        # 1. Detect deployment mode
        deployment_info = await self.detect_deployment_mode(app_id, branch_name)
        results['checks']['deployment_mode'] = deployment_info
        
        # 2. Detect framework from package.json
        framework_info = await self.detect_framework_from_package_json(repo_path)
        results['checks']['framework'] = framework_info
        
        # 3. Check for amplify.yml
        amplify_yml_path = Path(repo_path) / 'amplify.yml'
        results['checks']['amplify_yml'] = {
            'exists': amplify_yml_path.exists(),
            'path': str(amplify_yml_path)
        }
        
        # 4. Check for package-lock.json
        package_lock_path = Path(repo_path) / 'package-lock.json'
        results['checks']['package_lock'] = {
            'exists': package_lock_path.exists(),
            'path': str(package_lock_path)
        }
        
        # 5. Check for GitHub Actions workflow
        workflow_dir = Path(repo_path) / '.github' / 'workflows'
        if workflow_dir.exists():
            workflows = list(workflow_dir.glob('*.yml')) + list(workflow_dir.glob('*.yaml'))
            amplify_workflows = [w for w in workflows if 'amplify' in w.name.lower()]
            results['checks']['github_workflows'] = {
                'exists': len(amplify_workflows) > 0,
                'files': [str(w) for w in amplify_workflows]
            }
        else:
            results['checks']['github_workflows'] = {
                'exists': False,
                'files': []
            }
        
        # 6. Determine recommended configuration
        deployment_mode = deployment_info.get('deployment_mode', 'unknown')
        
        if deployment_mode == 'repository':
            results['recommendations'] = {
                'deployment_strategy': 'repository-connected',
                'use_webhooks': False,
                'use_create_deployment': False,
                'auto_build': deployment_info.get('auto_build', False),
                'workflow_type': 'repository-connected',
                'notes': [
                    'App is connected to repository - automatic deployments will be triggered by Git pushes',
                    'No need for manual deployment triggers or webhooks',
                    'Ensure amplify.yml is in repository root',
                    'Backend deployment via npx ampx pipeline-deploy',
                    'Frontend will build automatically after push'
                ]
            }
        elif deployment_mode == 'manual':
            results['recommendations'] = {
                'deployment_strategy': 'manual',
                'use_webhooks': True,
                'use_create_deployment': True,
                'auto_build': False,
                'workflow_type': 'manual-deployment',
                'notes': [
                    'App is not connected to repository - manual deployments required',
                    'Can use webhooks and create-deployment API',
                    'GitHub Actions will handle all deployments',
                    'More control but more complex setup'
                ]
            }
        else:
            results['recommendations'] = {
                'deployment_strategy': 'unknown',
                'notes': ['Could not determine deployment mode - please check app configuration']
            }
        
        # 7. Overall status
        results['ready_for_deployment'] = (
            deployment_info.get('success', False) and
            framework_info.get('success', False) and
            results['checks']['package_lock']['exists']
        )
        
        return results


async def main():
    """Test the deployment detector"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python deployment_detector.py <app_id> <branch_name> [repo_path]")
        sys.exit(1)
    
    app_id = sys.argv[1]
    branch_name = sys.argv[2]
    repo_path = sys.argv[3] if len(sys.argv) > 3 else '.'
    
    detector = DeploymentDetector()
    
    # Run comprehensive check
    results = await detector.check_deployment_prerequisites(app_id, branch_name, repo_path)
    
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())