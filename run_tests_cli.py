#!/usr/bin/env python3
"""
CLI Test Runner for Agentic Trading

This script runs all tests directly within the agent session, bypassing
GitHub Actions workflows that require maintainer approval for external actors.

Usage:
    python run_tests_cli.py [--verbose] [--specific-test=test_name]
"""

import sys
import subprocess
import os
import time
from pathlib import Path
import argparse


class CliTestRunner:
    """CLI test runner that executes tests directly"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.project_root = Path(__file__).parent
        os.chdir(self.project_root)
        
        # Test files to run
        self.test_files = [
            'test_workflow.py',
            'test_prolog_generation.py', 
            'test_prolog_analysis.py',
            'test_failure_simulation.py'
        ]
        
        self.results = {}
        
    def log(self, message):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def install_dependencies(self):
        """Install required dependencies"""
        self.log("Installing Python dependencies...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True, capture_output=not self.verbose)
            self.log("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def check_system_dependencies(self):
        """Check if system dependencies are available"""
        self.log("Checking system dependencies...")
        
        # Check for SWI-Prolog
        try:
            subprocess.run(['swipl', '--version'], check=True, capture_output=True)
            self.log("✅ SWI-Prolog is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("⚠️  SWI-Prolog not found - some tests may fail")
        
        # Check for Playwright browsers
        try:
            # Try to install Playwright browsers
            subprocess.run([
                sys.executable, '-m', 'playwright', 'install', 'chromium'
            ], check=True, capture_output=not self.verbose)
            self.log("✅ Playwright browsers ready")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("⚠️  Playwright setup issue - browser tests may fail")
    
    def run_single_test(self, test_file):
        """Run a single test file and return results"""
        self.log(f"Running {test_file}...")
        
        start_time = time.time()
        try:
            result = subprocess.run([
                sys.executable, test_file
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            
            self.results[test_file] = {
                'success': success,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
            if success:
                print(f"✅ {test_file} - PASSED ({duration:.1f}s)")
            else:
                print(f"❌ {test_file} - FAILED ({duration:.1f}s)")
                if self.verbose:
                    print(f"   STDOUT: {result.stdout[:200]}...")
                    print(f"   STDERR: {result.stderr[:200]}...")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file} - TIMEOUT (exceeded 5 minutes)")
            self.results[test_file] = {
                'success': False,
                'duration': 300,
                'stdout': '',
                'stderr': 'Test timed out after 5 minutes',
                'returncode': -1
            }
            return False
        except Exception as e:
            print(f"❌ {test_file} - ERROR: {e}")
            self.results[test_file] = {
                'success': False,
                'duration': 0,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
            return False
    
    def run_github_models_test(self):
        """Test GitHub Models integration with mock token"""
        self.log("Testing GitHub Models integration...")
        
        try:
            # Set mock token for testing
            env = os.environ.copy()
            env['GITHUB_TOKEN'] = 'mock_token_for_testing'
            
            result = subprocess.run([
                sys.executable, '-c', '''
from github_models_analyzer_enhanced import GitHubModelsAnalyzer
analyzer = GitHubModelsAnalyzer()
print("✅ GitHub Models analyzer initialized successfully")
'''
            ], capture_output=True, text=True, env=env, timeout=30)
            
            success = result.returncode == 0
            
            if success:
                print("✅ GitHub Models integration - PASSED")
            else:
                print("❌ GitHub Models integration - FAILED")
                if self.verbose:
                    print(f"   Error: {result.stderr}")
            
            return success
            
        except Exception as e:
            print(f"❌ GitHub Models integration - ERROR: {e}")
            return False
    
    def run_all_tests(self, specific_test=None):
        """Run all tests or a specific test"""
        print("🧪 Starting CLI Test Runner")
        print("=" * 50)
        
        # Setup phase
        if not self.install_dependencies():
            return False
        
        self.check_system_dependencies()
        
        print("\n📋 Running Tests")
        print("-" * 30)
        
        all_passed = True
        tests_to_run = [specific_test] if specific_test else self.test_files
        
        # Run Python tests
        for test_file in tests_to_run:
            if test_file in self.test_files and os.path.exists(test_file):
                success = self.run_single_test(test_file)
                all_passed = all_passed and success
            elif specific_test:
                print(f"❌ Test file '{specific_test}' not found")
                return False
        
        # Run GitHub Models test if no specific test requested
        if not specific_test:
            github_models_success = self.run_github_models_test()
            all_passed = all_passed and github_models_success
        
        # Summary
        print("\n📊 Test Summary")
        print("-" * 30)
        
        passed_count = sum(1 for r in self.results.values() if r['success'])
        total_count = len(self.results)
        if not specific_test:
            total_count += 1  # Include GitHub Models test
            if github_models_success:
                passed_count += 1
        
        print(f"Tests passed: {passed_count}/{total_count}")
        
        if all_passed:
            print("🎉 All tests PASSED!")
        else:
            print("❌ Some tests FAILED")
            print("\nFailed tests:")
            for test_file, result in self.results.items():
                if not result['success']:
                    print(f"  • {test_file} (exit code: {result['returncode']})")
        
        return all_passed


def main():
    parser = argparse.ArgumentParser(description='Run tests directly via CLI')
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help='Enable verbose output')
    parser.add_argument('--specific-test', '-t', type=str,
                        help='Run a specific test file')
    
    args = parser.parse_args()
    
    runner = CliTestRunner(verbose=args.verbose)
    success = runner.run_all_tests(specific_test=args.specific_test)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()