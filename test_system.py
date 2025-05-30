#!/usr/bin/env python3
"""
Test script to validate SEC Analysis System functionality.
"""

import tempfile
import sys
from datetime import date, timedelta
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sec_analysis.models import Filing, MasterIndexEntry
from sec_analysis.parsers import MasterIndexParser
from sec_analysis.storage import FileManager
from sec_analysis.analyzers import MungerAnalyzer


def test_master_index_parsing():
    """Test master index parsing functionality."""
    print("Testing master index parsing...")
    
    # Sample master index content
    sample_content = """Form Type|Company Name|CIK|Date Filed|File Name
--------------------------------------------
10-K|APPLE INC|320193|2024-01-15|edgar/data/320193/0000320193-24-000006.txt
8-K|MICROSOFT CORP|789019|2024-01-15|edgar/data/789019/0000789019-24-000007.txt
10-Q|AMAZON COM INC|1018724|2024-01-15|edgar/data/1018724/0001018724-24-000003.txt"""
    
    parser = MasterIndexParser()
    entries = parser.parse_master_index(sample_content)
    
    assert len(entries) == 3, f"Expected 3 entries, got {len(entries)}"
    assert entries[0].company_name == "APPLE INC", f"Expected APPLE INC, got {entries[0].company_name}"
    assert entries[0].form_type == "10-K", f"Expected 10-K, got {entries[0].form_type}"
    
    print("✅ Master index parsing test passed!")
    return entries


def test_filing_conversion():
    """Test conversion from MasterIndexEntry to Filing."""
    print("Testing filing conversion...")
    
    entry = MasterIndexEntry(
        cik="320193",
        company_name="APPLE INC",
        form_type="10-K",
        date_filed="2024-01-15",
        filename="edgar/data/320193/0000320193-24-000006.txt"
    )
    
    filing = entry.to_filing()
    
    assert filing.cik == "0000320193", f"Expected padded CIK, got {filing.cik}"
    assert filing.company_name == "APPLE INC"
    assert filing.form_type == "10-K"
    assert "sec.gov" in filing.url
    
    print("✅ Filing conversion test passed!")
    return filing


def test_file_management():
    """Test file management and storage functionality."""
    print("Testing file management...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_manager = FileManager(temp_dir)
        
        # Test directory creation
        test_date = date(2024, 1, 15)
        daily_path = file_manager.get_daily_raw_path(test_date)
        assert "2024/01/15" in str(daily_path)
        
        # Test CIK directory
        cik_dir = file_manager.get_cik_directory(test_date, "0000320193")
        assert "CIK_0000320193" in str(cik_dir)
        
        # Test master index saving
        content = "test content"
        saved_path = file_manager.save_master_index(test_date, content)
        assert saved_path.exists()
        
        # Test filing metadata saving
        filing = Filing(
            cik="0000320193",
            company_name="APPLE INC",
            form_type="10-K",
            date_filed=test_date,
            filename="test.txt",
            url="https://example.com/test.txt"
        )
        
        metadata_path = file_manager.save_filing_metadata(filing, test_date)
        assert metadata_path.exists()
        assert metadata_path.suffix == ".parquet"
    
    print("✅ File management test passed!")


def test_munger_analysis():
    """Test Munger analysis functionality."""
    print("Testing Munger analysis...")
    
    filing = Filing(
        cik="0000320193",
        company_name="APPLE INC",
        form_type="10-K",
        date_filed=date(2024, 1, 15),
        filename="test.txt",
        url="https://example.com/test.txt"
    )
    
    # Sample filing content
    filing_content = """
    APPLE INC
    FORM 10-K
    
    BUSINESS OVERVIEW
    Apple Inc. designs, manufactures and markets mobile communication and media devices...
    
    FINANCIAL STATEMENTS
    Revenue: $365,817 million
    Net income: $94,680 million
    Total assets: $365,725 million
    """
    
    analyzer = MungerAnalyzer()
    analysis = analyzer.analyze_company(filing, filing_content, market_price=150.0)
    
    assert analysis.cik == "0000320193"
    assert analysis.company_name == "APPLE INC"
    assert analysis.form_type == "10-K"
    assert len(analysis.valuation_scenarios) == 3
    assert analysis.version == "2.1"
    
    # Test margin of safety calculation
    analysis.update_margin_of_safety()
    assert analysis.margin_of_safety is not None
    
    print("✅ Munger analysis test passed!")
    return analysis


def test_analysis_storage():
    """Test analysis result storage."""
    print("Testing analysis storage...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_manager = FileManager(temp_dir)
        
        # Create a sample analysis
        filing = Filing(
            cik="0000320193",
            company_name="APPLE INC",
            form_type="10-K",
            date_filed=date(2024, 1, 15),
            filename="test.txt",
            url="https://example.com/test.txt"
        )
        
        analyzer = MungerAnalyzer()
        analysis = analyzer.analyze_company(filing, "sample content", market_price=150.0)
        
        # Save analysis
        saved_path = file_manager.save_analysis_result(analysis)
        assert saved_path.exists()
        assert saved_path.suffix == ".json"
        
        # Check that markdown report was also created
        md_file = saved_path.parent / f"{analysis.company_name.replace(' ', '_')}_{analysis.analysis_date.strftime('%Y%m%d')}_munger.md"
        assert md_file.exists()
        
        # Test loading analysis back
        loaded_analysis = file_manager.load_analysis_result(saved_path)
        assert loaded_analysis.cik == analysis.cik
        assert loaded_analysis.company_name == analysis.company_name
    
    print("✅ Analysis storage test passed!")


def run_all_tests():
    """Run all test functions."""
    print("🚀 Starting SEC Analysis System Tests\n")
    
    try:
        test_master_index_parsing()
        test_filing_conversion()
        test_file_management()
        test_munger_analysis()
        test_analysis_storage()
        
        print("\n🎉 All tests passed! SEC Analysis System is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)