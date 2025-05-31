# Test Failure Simulation Documentation

This file is created specifically to test the CI/CD failure handling workflow.

## Test Scenario

When a commit message contains "test-failure-simulation", the following should happen:

1. **Failure Detection**: The `test_failure_simulation.py` script will detect the trigger and intentionally fail
2. **Issue Creation**: The CI/CD workflow should create a GitHub issue on behalf of adamrybinski
3. **AI Enhancement**: If GitHub Models is available, an AI-enhanced failure summary should be generated
4. **Copilot Triggering**: The issue should include @copilot mention to trigger the next agent session
5. **Proper Attribution**: The issue should be assigned to adamrybinski with contact info adam@compose.systems

This tests the complete failure handling pipeline from detection to agent triggering.