# Copilot Agent Testing Guide

This document explains how to run tests directly within agent sessions, bypassing GitHub Actions workflows that require maintainer approval.

## Problem Statement

GitHub Actions workflows triggered by external actors (like @copilot) require manual approval from maintainers for security reasons. This creates delays in the development process when agents need to run tests to validate their changes.

## Solution: CLI-Based Testing

Instead of relying on GitHub Actions, we've created CLI-based testing tools that can be run directly within agent sessions.

## Available Tools

### 1. Full CLI Test Runner (`run_tests_cli.py`)

A comprehensive test runner that mimics the behavior of the GitHub Actions workflow.

```bash
# Run all tests
python run_tests_cli.py

# Run with verbose output
python run_tests_cli.py --verbose

# Run a specific test
python run_tests_cli.py --specific-test=test_workflow.py
```

### 2. Quick Test Utilities (`copilot_test_utils.py`)

Python functions that can be imported and used directly in agent sessions.

```python
from copilot_test_utils import test_all, test_workflow, test_prolog

# Run all tests
success = test_all()

# Run specific test suites
test_workflow()
test_prolog()

# Or use the underlying functions for custom control
from copilot_test_utils import run_quick_tests, print_test_results

results = run_quick_tests(verbose=True)
print_test_results(results)
```

## Features

### Automatic Dependency Management
- Installs Python dependencies from `requirements.txt`
- Sets up Playwright browsers
- Checks for system dependencies (SWI-Prolog)

### Comprehensive Test Coverage
- Workflow functionality tests
- Prolog generation and analysis tests
- GitHub Models integration tests
- Failure simulation tests

### Progress Reporting
- Real-time test execution status
- Detailed error reporting
- Summary of pass/fail rates
- Execution timing

### Error Handling
- Timeout protection (5-10 minutes per test)
- Graceful failure handling
- Detailed error messages

## Usage in Agent Sessions

When working on the repository, agents can now:

1. **Validate changes immediately**:
   ```python
   from copilot_test_utils import test_all
   test_all()  # Runs all tests and reports results
   ```

2. **Test specific components**:
   ```python
   from copilot_test_utils import test_workflow
   test_workflow()  # Focus on workflow-related tests
   ```

3. **Debug specific issues**:
   ```bash
   python run_tests_cli.py --verbose --specific-test=test_prolog_analysis.py
   ```

## Integration with Development Workflow

### For Code Changes
1. Make code changes
2. Run relevant tests using CLI tools
3. Fix any failures
4. Commit changes with confidence

### For PR Comments
When @copilot is mentioned in PR comments:
1. Agent analyzes the request
2. Makes necessary changes
3. Runs tests using CLI tools to validate
4. Posts results in PR comments
5. Commits changes if tests pass

## Migration from GitHub Actions

### Before (GitHub Actions)
- Triggered by PR comments
- Required maintainer approval
- Delays in feedback
- Complex YAML workflow management

### After (CLI Testing)
- Immediate execution within agent sessions
- No approval required
- Instant feedback
- Simple Python scripts

## Example Session Flow

```python
# 1. Import testing utilities
from copilot_test_utils import test_all, test_workflow

# 2. Run tests before making changes
print("Running baseline tests...")
if not test_all():
    print("⚠️ Some tests are already failing")

# 3. Make code changes
# ... code modifications ...

# 4. Validate changes
print("Testing changes...")
if test_workflow():
    print("✅ Workflow tests pass - safe to commit")
else:
    print("❌ Tests failed - need to fix issues")

# 5. Commit if tests pass
```

## Benefits

1. **Immediate Feedback**: No waiting for workflow approvals
2. **Agent Independence**: Agents can validate their own changes
3. **Faster Development**: Immediate test execution
4. **Better Debugging**: Verbose output and detailed error reporting
5. **Flexible Testing**: Run all tests or focus on specific areas

## Future Enhancements

- Integration with MCP (Model Context Protocol) tools
- Automated test selection based on changed files
- Performance benchmarking
- Test result caching
- Integration with code coverage tools

## Support

If you encounter issues with the CLI testing tools:

1. Check that all dependencies are installed correctly
2. Ensure SWI-Prolog is available for Prolog tests
3. Verify Playwright browsers are installed
4. Run with `--verbose` flag for detailed debugging information

The CLI tools are designed to be self-contained and should work in any environment where the repository dependencies can be installed.