#!/usr/bin/env python3
"""
Agent Session Completion Trigger

This utility can be called from within agent sessions to trigger
post-session testing and commenting workflows.
"""

import os
import sys
import requests
import json
from pathlib import Path


class AgentSessionTrigger:
    """Triggers GitHub Actions workflows for post-session testing"""
    
    def __init__(self, token=None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN environment variable or pass token parameter.")
        
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        # Try to detect repo info from git
        self.repo_owner = 'adamrybinski'
        self.repo_name = 'agentic-trading'
    
    def get_current_branch(self):
        """Get the current git branch name"""
        try:
            import subprocess
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception:
            return 'main'  # fallback
    
    def get_current_commit(self):
        """Get the current git commit hash"""
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception:
            return 'unknown'
    
    def trigger_post_session_tests(self, pr_number, session_context=None, branch_name=None):
        """
        Trigger the post-session testing workflow
        
        Args:
            pr_number (str|int): PR number to comment on
            session_context (str): Description of what the session accomplished
            branch_name (str): Branch name to test (auto-detected if not provided)
        
        Returns:
            dict: Response from GitHub API
        """
        if not branch_name:
            branch_name = self.get_current_branch()
        
        if not session_context:
            session_context = f"Agent session completed on branch {branch_name}"
        
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/agent-session-completion.yml/dispatches"
        
        payload = {
            'ref': branch_name,
            'inputs': {
                'pr_number': str(pr_number),
                'branch_name': branch_name,
                'session_context': session_context
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 204:
                return {
                    'success': True,
                    'message': f"Successfully triggered post-session tests for PR #{pr_number}",
                    'branch': branch_name,
                    'context': session_context
                }
            else:
                return {
                    'success': False,
                    'message': f"Failed to trigger workflow: {response.status_code} - {response.text}",
                    'response': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Error triggering workflow: {str(e)}"
            }
    
    def schedule_completion_comment(self, pr_number, session_summary=None):
        """
        Schedule a completion comment to be posted after session ends
        
        This is the main function to call before ending an agent session.
        
        Args:
            pr_number (str|int): PR number to comment on
            session_summary (str): Summary of what was accomplished in the session
        
        Returns:
            dict: Result of the trigger attempt
        """
        branch = self.get_current_branch()
        commit = self.get_current_commit()[:7]
        
        if not session_summary:
            session_summary = f"Agent session completed - changes ready for testing (commit: {commit})"
        
        print(f"🤖 Scheduling post-session tests for PR #{pr_number}")
        print(f"📋 Branch: {branch}")
        print(f"🔧 Context: {session_summary}")
        print(f"⏳ Tests will start in 30 seconds after this call...")
        
        result = self.trigger_post_session_tests(
            pr_number=pr_number,
            session_context=session_summary,
            branch_name=branch
        )
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"📊 Check the Actions tab for workflow progress")
            print(f"💬 adamrybinski will comment on PR #{pr_number} with results")
        else:
            print(f"❌ {result['message']}")
        
        return result


def trigger_completion_tests(pr_number, session_summary=None):
    """
    Convenience function to trigger post-session tests
    
    Args:
        pr_number (str|int): PR number to comment on  
        session_summary (str): What was accomplished in the session
    
    Returns:
        bool: True if successfully triggered, False otherwise
    """
    try:
        trigger = AgentSessionTrigger()
        result = trigger.schedule_completion_comment(pr_number, session_summary)
        return result['success']
    except Exception as e:
        print(f"❌ Error triggering completion tests: {e}")
        return False


def main():
    """CLI interface for triggering completion tests"""
    if len(sys.argv) < 2:
        print("Usage: python agent_session_trigger.py <pr_number> [session_summary]")
        print("Example: python agent_session_trigger.py 19 'Fixed test failures and updated workflows'")
        sys.exit(1)
    
    pr_number = sys.argv[1]
    session_summary = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = trigger_completion_tests(pr_number, session_summary)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()