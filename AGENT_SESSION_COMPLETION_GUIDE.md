# Agent Session Completion Guide

This document explains how to use the new agent session completion workflow that triggers post-session testing and comments as adamrybinski.

## Overview

The agent session completion system allows you to:
1. **Trigger tests programmatically** from within agent sessions
2. **Wait 30 seconds** for the session to finish before running tests
3. **Comment as adamrybinski** with test results on the PR
4. **Run tests on the latest code** from the session

## Quick Usage

### From Python (Recommended)
```python
from copilot_test_utils import complete_session

# At the end of an agent session:
complete_session(pr_number=19, session_summary="Fixed workflow issues and added new testing tools")
```

### From Command Line
```bash
python agent_session_trigger.py 19 "Fixed workflow issues and added new testing tools"
```

### Simple Trigger (No Summary)
```python
from copilot_test_utils import trigger_post_session_tests

trigger_post_session_tests(19)
```

## How It Works

1. **Agent calls completion function** before ending the session
2. **GitHub Actions workflow is triggered** via `workflow_dispatch`
3. **Workflow waits 30 seconds** for session to complete
4. **Tests run automatically** on the latest code from the session
5. **adamrybinski comments** on the PR with results

## Workflow Details

### Success Comment Example
```
## ✅ Post-Session Test Results

Just finished running comprehensive tests after the agent session. Everything looks good!

### 📊 Test Summary
- **Workflow Tests**: ✅ Passed
- **Prolog Generation**: ✅ Passed  
- **Prolog Analysis**: ✅ Passed
- **GitHub Models**: ✅ Passed
- **Failure Simulation**: ✅ Passed

### 📋 Session Details
- **Branch**: `feature-branch`
- **Commit**: `abc123f`
- **Session Context**: Fixed workflow issues and added new testing tools
- **Completed**: 12/8/2024, 3:45:23 PM

The changes from the agent session are working correctly and all tests are passing. Ready for review! 🚀
```

### Failure Comment Example
```
## ❌ Post-Session Test Failures

Found some issues after the agent session completed. Here's what needs attention:

### 📋 Session Details  
- **Branch**: `feature-branch`
- **Commit**: `abc123f`
- **Session Context**: Fixed workflow issues and added new testing tools
- **Failed**: 12/8/2024, 3:45:23 PM

### 🔍 Failure Analysis
The tests ran automatically after the 30-second delay, but some components aren't working as expected.

Let me take a look at what went wrong and fix the issues. @copilot please analyze the test failures.
```

## Requirements

### Environment Variables
- `GITHUB_TOKEN`: Required for triggering workflows
- `ADAMRYBINSKI_TOKEN`: (Optional) Personal access token for commenting as adamrybinski

### Repository Secrets
For the workflow to comment as adamrybinski, you need to add a repository secret:
- `ADAMRYBINSKI_TOKEN`: Personal access token with `repo` and `write:discussion` permissions

If this secret is not set, the workflow will fall back to using the default `GITHUB_TOKEN` (comments will appear from GitHub Actions bot).

## Files Created

1. **`.github/workflows/agent-session-completion.yml`** - The workflow that runs tests and comments
2. **`agent_session_trigger.py`** - Python utility for triggering the workflow
3. **`copilot_test_utils.py`** - Updated with convenience functions

## Integration with Existing Workflows

This new system complements the existing `copilot-triggered-tests.yml` workflow:

- **Existing workflow**: Triggered by PR comments, runs immediately
- **New workflow**: Triggered programmatically from agent sessions, waits 30 seconds, comments as adamrybinski

Both workflows run the same comprehensive test suite but serve different purposes:
- Use existing workflow for interactive testing during development
- Use new workflow for automated testing after agent sessions complete

## Example Agent Session Flow

```python
# During agent session - make changes to code
# ...

# Before ending the session:
from copilot_test_utils import complete_session

complete_session(
    pr_number=19, 
    session_summary="Updated workflows to support agent session completion with proper commenting as adamrybinski"
)

# Agent session ends
# 30 seconds later: tests run automatically
# Results are commented on PR #19 as adamrybinski
```

## Troubleshooting

### Workflow Not Triggering
- Check that `GITHUB_TOKEN` is available in the environment
- Verify the PR number is correct
- Check GitHub Actions tab for any dispatch failures

### Comments Appear as GitHub Actions Bot
- Add `ADAMRYBINSKI_TOKEN` repository secret
- Ensure the token has appropriate permissions

### Tests Failing
- Check the workflow logs in the Actions tab
- Tests run on the branch/commit that was current when triggered
- Make sure all changes were committed before triggering

## Security Notes

- The `ADAMRYBINSKI_TOKEN` secret should be a personal access token with minimal required permissions
- Only trusted users should be able to trigger this workflow
- The workflow runs on the specified branch, so ensure code integrity before triggering