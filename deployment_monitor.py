#!/usr/bin/env python3
"""
Deployment Monitoring for AWS Amplify Apps

This module provides enhanced monitoring capabilities for Amplify deployments,
with better error detection and automatic issue resolution.
"""

import json
import logging
import asyncio
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DeploymentMonitor:
    """Monitor and analyze Amplify deployments"""
    
    def __init__(self, aws_region: str = 'eu-north-1'):
        self.aws_region = aws_region
        self.common_errors = {
            'npm ci': {
                'pattern': r'npm ci.*failed|npm ERR!.*package-lock\.json',
                'fix': 'regenerate_package_lock',
                'description': 'Package lock file out of sync'
            },
            'typescript': {
                'pattern': r'TypeScript error|TS\d{4}:|type.*error',
                'fix': 'fix_typescript_errors',
                'description': 'TypeScript compilation errors'
            },
            'eslint': {
                'pattern': r'ESLint.*error|Parsing error:|Linting failed',
                'fix': 'fix_linting_issues',
                'description': 'ESLint/formatting issues'
            },
            'missing_outputs': {
                'pattern': r'amplify_outputs\.json.*not found|Cannot find.*amplify_outputs',
                'fix': 'generate_outputs',
                'description': 'Missing amplify_outputs.json'
            },
            'build_failed': {
                'pattern': r'npm run build.*failed|Build failed|next build.*error',
                'fix': 'analyze_build_error',
                'description': 'Build command failed'
            },
            'wrong_deployment_mode': {
                'pattern': r'Operation not supported.*repository|BadRequestException.*CreateDeployment',
                'fix': 'use_repository_connected_workflow',
                'description': 'Wrong deployment mode for repository-connected app'
            }
        }
    
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
    
    async def monitor_amplify_job(
        self,
        app_id: str,
        branch_name: str,
        job_id: Optional[str] = None,
        commit_sha: Optional[str] = None,
        timeout_seconds: int = 1800,  # 30 minutes
        check_interval: int = 30
    ) -> Dict[str, Any]:
        """
        Monitor an Amplify job with enhanced error detection
        
        Args:
            app_id: Amplify app ID
            branch_name: Branch name
            job_id: Specific job ID to monitor (optional)
            commit_sha: Commit SHA to find job (optional)
            timeout_seconds: Maximum time to wait
            check_interval: Seconds between checks
        
        Returns:
            Dict with job status, errors, and suggested fixes
        """
        logger.info(f"Monitoring Amplify job for app {app_id} branch {branch_name}")
        
        start_time = asyncio.get_event_loop().time()
        
        # If no job_id, try to find it
        if not job_id:
            if commit_sha:
                job_id = await self.find_job_by_commit(app_id, branch_name, commit_sha)
            else:
                job_id = await self.get_latest_job(app_id, branch_name)
        
        if not job_id:
            return {
                'success': False,
                'error': 'No job found to monitor',
                'suggestion': 'Job may not have started yet. Check Amplify Console.'
            }
        
        logger.info(f"Monitoring job {job_id}")
        
        while asyncio.get_event_loop().time() - start_time < timeout_seconds:
            # Get job details
            cmd = [
                'aws', 'amplify', 'get-job',
                '--app-id', app_id,
                '--branch-name', branch_name,
                '--job-id', job_id,
                '--region', self.aws_region
            ]
            
            result = await self.run_command(cmd)
            
            if not result['success']:
                logger.warning(f"Could not get job status: {result.get('stderr', '')}")
                await asyncio.sleep(check_interval)
                continue
            
            try:
                job_data = json.loads(result['stdout'])
                job = job_data.get('job', {})
                summary = job.get('summary', {})
                status = summary.get('status', 'UNKNOWN')
                
                logger.info(f"Job status: {status}")
                
                if status == 'SUCCEED':
                    return {
                        'success': True,
                        'job_id': job_id,
                        'status': 'SUCCEED',
                        'duration': summary.get('duration'),
                        'app_url': self.extract_app_url(job),
                        'message': 'Deployment completed successfully'
                    }
                
                elif status in ['FAILED', 'CANCELLED']:
                    # Analyze failure
                    error_analysis = self.analyze_job_failure(job)
                    
                    return {
                        'success': False,
                        'job_id': job_id,
                        'status': status,
                        'error': error_analysis['error'],
                        'error_type': error_analysis['type'],
                        'suggested_fix': error_analysis['fix'],
                        'failed_step': error_analysis['failed_step'],
                        'logs': error_analysis['logs']
                    }
                
                elif status in ['PENDING', 'PROVISIONING', 'RUNNING']:
                    # Still running
                    current_step = self.get_current_step(job)
                    if current_step:
                        logger.info(f"Current step: {current_step}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse job data: {e}")
            
            await asyncio.sleep(check_interval)
        
        return {
            'success': False,
            'job_id': job_id,
            'status': 'TIMEOUT',
            'error': 'Job monitoring timeout',
            'suggestion': 'Check Amplify Console for current status'
        }
    
    async def find_job_by_commit(self, app_id: str, branch_name: str, commit_sha: str) -> Optional[str]:
        """Find a job ID by commit SHA"""
        cmd = [
            'aws', 'amplify', 'list-jobs',
            '--app-id', app_id,
            '--branch-name', branch_name,
            '--max-items', '10',
            '--region', self.aws_region
        ]
        
        result = await self.run_command(cmd)
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                jobs = data.get('jobSummaries', [])
                
                for job in jobs:
                    if job.get('commitId', '').startswith(commit_sha[:7]):
                        return job.get('jobId')
            except:
                pass
        
        return None
    
    async def get_latest_job(self, app_id: str, branch_name: str) -> Optional[str]:
        """Get the latest job ID for a branch"""
        cmd = [
            'aws', 'amplify', 'list-jobs',
            '--app-id', app_id,
            '--branch-name', branch_name,
            '--max-items', '1',
            '--region', self.aws_region
        ]
        
        result = await self.run_command(cmd)
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                jobs = data.get('jobSummaries', [])
                if jobs:
                    return jobs[0].get('jobId')
            except:
                pass
        
        return None
    
    def extract_app_url(self, job: Dict[str, Any]) -> Optional[str]:
        """Extract app URL from job data"""
        steps = job.get('steps', [])
        for step in steps:
            if step.get('stepName') == 'DEPLOY':
                artifacts = step.get('artifacts', {})
                return artifacts.get('appArtifactUrl')
        return None
    
    def get_current_step(self, job: Dict[str, Any]) -> Optional[str]:
        """Get the currently running step"""
        steps = job.get('steps', [])
        for step in steps:
            if step.get('status') == 'RUNNING':
                return step.get('stepName')
        return None
    
    def analyze_job_failure(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze job failure and suggest fixes"""
        result = {
            'error': 'Unknown error',
            'type': 'unknown',
            'fix': None,
            'failed_step': None,
            'logs': []
        }
        
        steps = job.get('steps', [])
        
        # Find failed step
        for step in steps:
            if step.get('status') == 'FAILED':
                result['failed_step'] = step.get('stepName')
                
                # Get error from step
                artifacts = step.get('artifacts', {})
                logs = artifacts.get('logs', '')
                result['logs'] = logs[:2000] if logs else []
                
                # Get error reason
                reason = step.get('reason', '')
                if reason:
                    result['error'] = reason
                
                # Check against known error patterns
                for error_type, error_info in self.common_errors.items():
                    if re.search(error_info['pattern'], logs, re.IGNORECASE):
                        result['type'] = error_type
                        result['fix'] = error_info['fix']
                        result['error'] = error_info['description']
                        break
                
                break
        
        # Special handling for deployment mode errors
        if 'Operation not supported' in str(result['logs']):
            result['type'] = 'wrong_deployment_mode'
            result['fix'] = 'use_repository_connected_workflow'
            result['error'] = 'App is repository-connected, cannot use manual deployment'
        
        return result
    
    async def auto_fix_error(
        self,
        error_type: str,
        app_id: str,
        branch_name: str,
        repo_path: str
    ) -> Dict[str, Any]:
        """Attempt to automatically fix common errors"""
        
        fixes_applied = []
        
        if error_type == 'regenerate_package_lock':
            logger.info("Regenerating package-lock.json...")
            await self.run_command(['npm', 'install'], cwd=repo_path)
            fixes_applied.append('Regenerated package-lock.json')
            
        elif error_type == 'fix_typescript_errors':
            logger.info("Attempting to fix TypeScript errors...")
            # Try to run type checking with fix
            await self.run_command(['npx', 'tsc', '--noEmit'], cwd=repo_path)
            fixes_applied.append('Checked TypeScript errors (manual fix may be needed)')
            
        elif error_type == 'fix_linting_issues':
            logger.info("Fixing linting issues...")
            await self.run_command(['npm', 'run', 'lint', '--', '--fix'], cwd=repo_path)
            fixes_applied.append('Fixed linting issues')
            
        elif error_type == 'generate_outputs':
            logger.info("Generating amplify_outputs.json...")
            await self.run_command([
                'npx', 'ampx', 'generate', 'outputs',
                '--branch', branch_name,
                '--app-id', app_id
            ], cwd=repo_path)
            fixes_applied.append('Generated amplify_outputs.json')
            
        elif error_type == 'wrong_deployment_mode':
            return {
                'success': False,
                'error': 'Wrong deployment mode',
                'message': 'This app is repository-connected. Use repository-connected workflow instead.',
                'action_required': 'Update GitHub Actions workflow to use repository-connected template'
            }
        
        if fixes_applied:
            # Commit and push fixes
            await self.run_command(['git', 'add', '-A'], cwd=repo_path)
            await self.run_command([
                'git', 'commit', '-m', f"Auto-fix: {', '.join(fixes_applied)}"
            ], cwd=repo_path)
            await self.run_command(['git', 'push'], cwd=repo_path)
            
            return {
                'success': True,
                'fixes_applied': fixes_applied,
                'message': 'Fixes applied and pushed. New build will be triggered.'
            }
        
        return {
            'success': False,
            'message': 'No automatic fix available for this error'
        }
    
    async def wait_for_job_to_start(
        self,
        app_id: str,
        branch_name: str,
        commit_sha: Optional[str] = None,
        max_wait_seconds: int = 120
    ) -> Optional[str]:
        """Wait for a job to start and return its ID"""
        
        logger.info("Waiting for Amplify job to start...")
        
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < max_wait_seconds:
            if commit_sha:
                job_id = await self.find_job_by_commit(app_id, branch_name, commit_sha)
            else:
                job_id = await self.get_latest_job(app_id, branch_name)
            
            if job_id:
                logger.info(f"Job started: {job_id}")
                return job_id
            
            await asyncio.sleep(5)
        
        logger.warning("Job did not start within timeout period")
        return None