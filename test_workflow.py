#!/usr/bin/env python3
"""
Test script for the daily SEC analysis workflow.

This script validates that the complete workflow functions correctly
with all the components: GitHub workflow, daily analysis, and LLM integration.
"""

import os
import sys
import tempfile
import asyncio
from pathlib import Path
from datetime import date, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from daily_analysis import DailyAnalysisOrchestrator


def test_prompt_loading():
    """Test that Charlie Munger prompts are properly loaded."""
    print("🧪 Testing prompt loading...")
    
    orchestrator = DailyAnalysisOrchestrator()
    
    assert orchestrator.system_prompt, "System prompt should not be empty"
    assert orchestrator.user_prompt_template, "User prompt template should not be empty"
    assert "Charlie Munger" in orchestrator.system_prompt, "System prompt should mention Charlie Munger"
    assert "{company_name}" in orchestrator.user_prompt_template, "User prompt should have placeholders"
    
    print("✅ Prompt loading test passed!")


def test_github_models_integration():
    """Test GitHub Models integration (without actual API calls)."""
    print("🧪 Testing GitHub Models integration...")
    
    orchestrator = DailyAnalysisOrchestrator()
    
    # Should detect absence of GitHub token
    assert not orchestrator._has_github_models_access(), "Should detect missing GITHUB_TOKEN"
    
    # Test with mock token
    os.environ['GITHUB_TOKEN'] = 'mock_token'
    orchestrator_with_token = DailyAnalysisOrchestrator()
    assert orchestrator_with_token._has_github_models_access(), "Should detect present GITHUB_TOKEN"
    
    # Clean up
    del os.environ['GITHUB_TOKEN']
    
    print("✅ GitHub Models integration test passed!")


def test_analysis_detection():
    """Test existing analysis detection."""
    print("🧪 Testing analysis detection...")
    
    orchestrator = DailyAnalysisOrchestrator()
    
    # Test with known existing date
    existing_date = date(2025, 5, 29)
    assert orchestrator._is_analysis_complete(existing_date), "Should detect existing analysis for 2025-05-29"
    
    # Test with non-existing date
    future_date = date(2025, 12, 31)
    assert not orchestrator._is_analysis_complete(future_date), "Should not detect analysis for future date"
    
    print("✅ Analysis detection test passed!")


async def test_workflow_execution():
    """Test the complete workflow execution (with minimal processing)."""
    print("🧪 Testing complete workflow execution...")
    
    orchestrator = DailyAnalysisOrchestrator()
    
    # Test with existing analysis (should skip and use existing)
    test_date = date(2025, 5, 29)
    
    try:
        summary = await orchestrator.run_daily_analysis(test_date, max_companies=1)
        
        assert isinstance(summary, dict), "Summary should be a dictionary"
        assert 'date' in summary, "Summary should contain date"
        assert 'total_companies' in summary, "Summary should contain total companies"
        assert 'successfully_analyzed' in summary, "Summary should contain success count"
        assert summary['total_companies'] > 0, "Should have found companies"
        
        print(f"✅ Workflow execution test passed! Summary: {summary}")
        
    except Exception as e:
        print(f"❌ Workflow execution test failed: {e}")
        raise


def test_workflow_yaml_structure():
    """Test GitHub Actions workflow YAML structure."""
    print("🧪 Testing workflow YAML structure...")
    
    import yaml
    
    workflow_path = Path(__file__).parent / '.github' / 'workflows' / 'daily-reports.yml'
    assert workflow_path.exists(), "Workflow file should exist"
    
    with open(workflow_path, 'r') as f:
        workflow = yaml.safe_load(f)
    
    assert workflow['name'] == "Daily SEC Analysis Reports", "Workflow name should be correct"
    
    on_section = workflow.get('on', {})
    assert 'schedule' in on_section, "Workflow should have schedule trigger"
    assert 'workflow_dispatch' in on_section, "Workflow should have manual trigger"
    
    schedule = on_section['schedule'][0]
    assert 'cron' in schedule, "Schedule should have cron expression"
    assert schedule['cron'] == '0 6 * * *', "Should run daily at 6 AM UTC"
    
    inputs = on_section['workflow_dispatch']['inputs']
    assert 'target_date' in inputs, "Should accept target_date input"
    assert 'max_companies' in inputs, "Should accept max_companies input"
    
    jobs = workflow.get('jobs', {})
    assert 'daily-analysis' in jobs, "Should have daily-analysis job"
    
    print("✅ Workflow YAML structure test passed!")


async def run_all_tests():
    """Run all tests."""
    print("🚀 Starting Daily SEC Analysis Workflow Tests\n")
    
    try:
        test_prompt_loading()
        test_github_models_integration()
        test_analysis_detection()
        await test_workflow_execution()
        test_workflow_yaml_structure()
        
        print("\n🎉 All tests passed! Daily SEC Analysis Workflow is ready.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)