#!/usr/bin/env python3
"""
Quick Test Functions for Copilot Agent Sessions

This module provides simple functions that can be imported and used
directly within agent sessions to run tests without GitHub Actions.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_quick_tests(verbose=False):
    """
    Run all tests quickly and return results.
    
    Args:
        verbose (bool): Enable verbose output
        
    Returns:
        dict: Test results with success status and details
    """
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Run the CLI test runner
    cmd = [sys.executable, 'run_tests_cli.py']
    if verbose:
        cmd.append('--verbose')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Tests timed out after 10 minutes',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'returncode': -1
        }


def run_specific_test(test_name, verbose=False):
    """
    Run a specific test file.
    
    Args:
        test_name (str): Name of the test file to run
        verbose (bool): Enable verbose output
        
    Returns:
        dict: Test results with success status and details
    """
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    cmd = [sys.executable, 'run_tests_cli.py', f'--specific-test={test_name}']
    if verbose:
        cmd.append('--verbose')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': f'Test {test_name} timed out after 5 minutes',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'returncode': -1
        }


def print_test_results(results):
    """Print test results in a nice format"""
    if results['success']:
        print("🎉 Tests PASSED!")
    else:
        print("❌ Tests FAILED!")
    
    if results['output']:
        print("\nOutput:")
        print(results['output'])
    
    if results['error']:
        print("\nErrors:")
        print(results['error'])


# Convenience functions for common use cases
def test_all():
    """Run all tests and print results"""
    print("Running all tests...")
    results = run_quick_tests(verbose=True)
    print_test_results(results)
    return results['success']


def test_workflow():
    """Run workflow tests specifically"""
    print("Running workflow tests...")
    results = run_specific_test('test_workflow.py', verbose=True)
    print_test_results(results)
    return results['success']


def test_prolog():
    """Run Prolog-related tests"""
    print("Running Prolog tests...")
    
    # Run both Prolog tests
    gen_results = run_specific_test('test_prolog_generation.py', verbose=True)
    analysis_results = run_specific_test('test_prolog_analysis.py', verbose=True)
    
    print("Prolog Generation Tests:")
    print_test_results(gen_results)
    
    print("\nProlog Analysis Tests:")
    print_test_results(analysis_results)
    
    return gen_results['success'] and analysis_results['success']


def trigger_post_session_tests(pr_number, session_summary=None):
    """
    Trigger post-session testing workflow that will comment as adamrybinski
    
    This should be called before ending an agent session to schedule
    automated testing and commenting on the PR.
    
    Args:
        pr_number (str|int): PR number to comment on
        session_summary (str): Summary of what was accomplished
        
    Returns:
        bool: True if successfully triggered, False otherwise
    """
    try:
        from agent_session_trigger import trigger_completion_tests
        return trigger_completion_tests(pr_number, session_summary)
    except ImportError:
        print("❌ agent_session_trigger module not found")
        return False
    except Exception as e:
        print(f"❌ Error triggering post-session tests: {e}")
        return False


def complete_session(pr_number, session_summary=None):
    """
    Complete an agent session by triggering post-session tests
    
    This is a convenience function that combines session completion
    with automatic test triggering.
    
    Args:
        pr_number (str|int): PR number to comment on
        session_summary (str): Summary of what was accomplished
    """
    print("🏁 Completing agent session...")
    
    if session_summary:
        print(f"📋 Session summary: {session_summary}")
    
    success = trigger_post_session_tests(pr_number, session_summary)
    
    if success:
        print("✅ Post-session tests scheduled successfully!")
        print("🔄 adamrybinski will comment with results in ~30 seconds")
    else:
        print("❌ Failed to schedule post-session tests")
    
    return success


if __name__ == '__main__':
    # If run directly, run all tests
    success = test_all()
    sys.exit(0 if success else 1)