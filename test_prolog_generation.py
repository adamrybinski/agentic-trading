#!/usr/bin/env python3
"""
Test Prolog generation with mock data
"""

from enhanced_sec_analysis import EnhancedSECAnalyzer
from sec_analysis.models import (
    AnalysisResult, MungerFilters, MoatDurabilityScore, ValuationScenario, 
    FinancialForensics
)
from datetime import date, datetime

def create_mock_analysis_result(cik: str, company_name: str) -> AnalysisResult:
    """Create a mock analysis result for testing."""
    return AnalysisResult(
        cik=cik,
        company_name=company_name,
        analysis_date=date(2025, 5, 30),
        filing_date=date(2025, 5, 29),
        form_type="10-K",
        
        # Moat Score
        moat_score=MoatDurabilityScore(
            market_share_stability=8.0,
            patent_portfolio_strength=7.5,
            customer_retention_rate=9.0,
            pricing_power_evidence=8.5
        ),
        
        # Financial Forensics
        financial_forensics=FinancialForensics(
            benford_law_score=7.5,
            capex_vs_depreciation_ratio=1.2,
            true_owner_earnings=5000000000.0,
            roe_5_year_avg=18.5,
            debt_equity_ratio=0.25,
            management_ownership_pct=8.5
        ),
        
        # Munger Filters
        munger_filters=MungerFilters(
            passes_all_filters=True,
            roe_above_15_for_5_years=True,
            debt_equity_below_8_percent=True,
            management_ownership_above_5_percent=True,
            consistent_earnings_growth=True
        ),
        
        # Valuation Scenarios
        valuation_scenarios=[
            ValuationScenario(
                scenario_name="Bear",
                discount_rate=0.12,
                terminal_growth_rate=0.02,
                intrinsic_value=45.0,
                dcf_value=44.0,
                graham_formula_value=46.0,
                earnings_power_value=45.5
            ),
            ValuationScenario(
                scenario_name="Base",
                discount_rate=0.10,
                terminal_growth_rate=0.025,
                intrinsic_value=60.0,
                dcf_value=59.0,
                graham_formula_value=61.0,
                earnings_power_value=60.5
            ),
            ValuationScenario(
                scenario_name="Bull",
                discount_rate=0.08,
                terminal_growth_rate=0.03,
                intrinsic_value=80.0,
                dcf_value=79.0,
                graham_formula_value=81.0,
                earnings_power_value=80.5
            )
        ],
        
        # Margin of Safety
        margin_of_safety=0.25,
        
        # Business Analysis
        business_model_changes=[],
        financial_anomalies=[],
        mental_model_conflicts=[]
    )

def main():
    """Test Prolog generation."""
    print("🧪 Testing Prolog generation with mock data...")
    
    analyzer = EnhancedSECAnalyzer()
    target_date = date(2025, 5, 30)
    
    # Create mock analysis results
    mock_results = [
        create_mock_analysis_result("0000320193", "Apple Inc"),
        create_mock_analysis_result("0000789019", "Microsoft Corp"),
        create_mock_analysis_result("0001652044", "Alphabet Inc")
    ]
    
    print(f"Generated {len(mock_results)} mock analysis results")
    
    # Generate Prolog summary
    try:
        analyzer._generate_prolog_summary(mock_results, target_date)
        print("✅ Prolog generation completed successfully")
        
        # Check if file was created
        prolog_file = analyzer.reports_path / "2025-05-30" / "munger_analysis_summary_20250530.md"
        if prolog_file.exists():
            print(f"✅ Prolog file created: {prolog_file}")
            print(f"📄 File size: {prolog_file.stat().st_size} bytes")
            
            # Show first few lines
            with open(prolog_file, 'r') as f:
                lines = f.readlines()
            
            print("\n📋 First 10 lines of Prolog file:")
            print("="*50)
            for i, line in enumerate(lines[:10]):
                print(f"{i+1:2d}: {line.rstrip()}")
            
            return True
        else:
            print("❌ Prolog file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error generating Prolog: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)