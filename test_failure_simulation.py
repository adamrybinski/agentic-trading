#!/usr/bin/env python3
"""
Test script to trigger failure scenarios for CI/CD testing
This simulates a failing test when specific conditions are met
"""

import sys
import os
import subprocess

def check_commit_message():
    """Check if the current commit message contains test failure trigger"""
    try:
        # Get the latest commit message
        result = subprocess.run(['git', 'log', '-1', '--pretty=%B'], 
                               capture_output=True, text=True, cwd='.')
        commit_msg = result.stdout.strip()
        
        return 'test-failure-simulation' in commit_msg.lower()
    except Exception:
        return False

def main():
    print("🧪 Running failure simulation test...")
    
    # Check environment variable trigger
    env_trigger = os.getenv("SIMULATE_FAILURE", "").lower() == "true"
    
    # Check commit message trigger
    commit_trigger = check_commit_message()
    
    # Check command line arguments
    arg_trigger = any('test-failure-simulation' in arg.lower() for arg in sys.argv)
    
    if env_trigger or commit_trigger or arg_trigger:
        print("🎭 FAILURE SIMULATION TRIGGERED!")
        print("This is an intentional failure to test:")
        print("  ✓ Issue creation on behalf of adamrybinski") 
        print("  ✓ AI-enhanced failure summary generation")
        print("  ✓ @copilot mention to trigger agent session")
        print("  ✓ Proper workflow failure handling")
        print("")
        print("❌ Simulated test failure - CI/CD workflow should create issue")
        raise SystemExit(1)
    else:
        print("✅ No failure trigger detected - test passes normally")
        print("To trigger failure simulation, use:")
        print("  - Set SIMULATE_FAILURE=true environment variable")
        print("  - Include 'test-failure-simulation' in commit message") 
        print("  - Pass 'test-failure-simulation' as argument")
        return 0

if __name__ == "__main__":
    main()