#!/usr/bin/env python3
"""
Test failure simulation script to test CI/CD failure handling
This script will intentionally fail when run to test the issue creation workflow
"""

import sys
import os

def main():
    print("🎭 Running test failure simulation...")
    print("This script is designed to fail to test the CI/CD failure workflow")
    
    # Check if this is a simulation run
    if "test-failure-simulation" in " ".join(sys.argv) or os.getenv("SIMULATE_FAILURE", "").lower() == "true":
        print("❌ Simulating test failure for CI/CD testing purposes")
        print("This failure should trigger:")
        print("1. Issue creation on behalf of adamrybinski")
        print("2. AI-enhanced failure summary")
        print("3. @copilot mention to trigger agent session")
        raise SystemExit(1)
    else:
        print("✅ Simulation not triggered - script would normally pass")
        return 0

if __name__ == "__main__":
    main()