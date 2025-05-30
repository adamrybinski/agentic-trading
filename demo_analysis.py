"""
Demo script for SEC Analysis System that works without internet access.

This script demonstrates the analysis system using mock data to show
how the system generates markdown reports and CSV summaries.
"""

import logging
import sys
import csv
from datetime import date, datetime
from typing import List, Dict, Any
from pathlib import Path
import json

from sec_analysis.models import Filing, AnalysisResult
from sec_analysis.storage import FileManager
from sec_analysis.analyzers import MungerAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('demo_analysis.log')
    ]
)

logger = logging.getLogger(__name__)


class DemoSECAnalysis:
    """Demo SEC Analysis System with mock data."""
    
    def __init__(self, base_storage_path: str = "sec_data"):
        """Initialize demo system."""
        self.file_manager = FileManager(base_storage_path)
        self.analyzer = MungerAnalyzer()
        self.analysis_results = []
        
        logger.info(f"Demo SEC Analysis System initialized with storage: {base_storage_path}")
    
    def create_mock_filings(self, target_date: date) -> List[Filing]:
        """Create mock filings for demonstration."""
        mock_companies = [
            {
                "cik": "0000320193",
                "company_name": "APPLE INC",
                "form_type": "10-K",
                "filename": "edgar/data/320193/0000320193-25-000001.txt"
            },
            {
                "cik": "0001318605", 
                "company_name": "TESLA INC",
                "form_type": "10-Q",
                "filename": "edgar/data/1318605/0001318605-25-000002.txt"
            },
            {
                "cik": "0001326801",
                "company_name": "META PLATFORMS INC",
                "form_type": "10-K", 
                "filename": "edgar/data/1326801/0001326801-25-000003.txt"
            },
            {
                "cik": "0000789019",
                "company_name": "MICROSOFT CORP",
                "form_type": "10-Q",
                "filename": "edgar/data/789019/0000789019-25-000004.txt"
            },
            {
                "cik": "0001045810",
                "company_name": "NVIDIA CORP",
                "form_type": "10-K",
                "filename": "edgar/data/1045810/0001045810-25-000005.txt"
            }
        ]
        
        filings = []
        for company in mock_companies:
            filing = Filing(
                cik=company["cik"],
                company_name=company["company_name"],
                form_type=company["form_type"],
                date_filed=target_date,
                filename=company["filename"],
                url=f"https://www.sec.gov/Archives/{company['filename']}"
            )
            filings.append(filing)
        
        logger.info(f"Created {len(filings)} mock filings for {target_date}")
        return filings
    
    def create_mock_filing_content(self, filing: Filing) -> str:
        """Create mock filing content for analysis."""
        content = f"""
UNITED STATES
SECURITIES AND EXCHANGE COMMISSION
Washington, D.C. 20549

FORM {filing.form_type}

ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934

For the fiscal year ended December 31, 2024

Commission File Number: 001-36743

{filing.company_name}
(Exact name of registrant as specified in its charter)

Delaware                                    47-0594463
(State of incorporation)                     (I.R.S. Employer Identification No.)

ITEM 1. BUSINESS

{filing.company_name} is a leading technology company that designs, manufactures, and markets innovative products and services. The company has established strong competitive moats through its brand loyalty, patent portfolio, and ecosystem of integrated products.

ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS

The company has demonstrated consistent financial performance with strong return on equity exceeding 15% for the past five consecutive years. Management maintains a conservative capital structure with debt-to-equity ratios below industry benchmarks.

The company continues to invest in research and development, strategic initiatives, and business transformation to maintain its competitive position. Recent acquisitions and new market entries have expanded the addressable market.

Key financial highlights include strong cash flow from operations, maintained pricing power despite competitive pressures, and growing market share in core segments.

ITEM 8. FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA

[This would contain detailed financial statements in a real filing]

Consolidated Statements of Operations
Net revenues: $394.3 billion
Net income: $97.0 billion
Earnings per share: $6.11

Consolidated Balance Sheets  
Total assets: $352.8 billion
Total debt: $28.5 billion
Shareholders' equity: $64.9 billion

Consolidated Statements of Cash Flows
Cash flow from operations: $104.0 billion
Capital expenditures: $10.9 billion
"""
        return content
    
    def run_demo_analysis(self, target_date: date, max_companies: int = 5) -> Dict[str, Any]:
        """Run complete demo analysis for a target date."""
        logger.info(f"Starting demo analysis for {target_date}")
        
        # Create mock filings
        filings = self.create_mock_filings(target_date)
        
        # Limit number of companies
        filings = filings[:max_companies]
        
        results = {
            'date': target_date,
            'total_filings': len(filings),
            'processed_filings': 0,
            'analyzed_filings': 0,
            'ciks_processed': set(),
            'errors': []
        }
        
        # Process each filing
        for filing in filings:
            try:
                logger.info(f"Processing {filing.company_name} ({filing.cik})")
                
                # Save filing metadata
                self.file_manager.save_filing_metadata(filing, target_date)
                results['processed_filings'] += 1
                results['ciks_processed'].add(filing.cik)
                
                # Create mock filing content
                filing_content = self.create_mock_filing_content(filing)
                
                # Save filing content
                self.file_manager.save_filing(filing, target_date, filing_content)
                
                # Perform Munger analysis
                analysis_result = self.analyzer.analyze_company(
                    filing, filing_content, market_price=150.0  # Mock market price
                )
                
                # Save analysis results (JSON and Markdown)
                self.file_manager.save_analysis_result(analysis_result)
                
                # Store for CSV summary
                self.analysis_results.append(analysis_result)
                
                results['analyzed_filings'] += 1
                logger.info(f"Analysis completed for {filing.company_name}")
                
            except Exception as e:
                error_msg = f"Error processing {filing.cik}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Update company database
        self.file_manager.update_company_database(filings)
        
        # Generate CSV summary
        self.generate_csv_summary(target_date)
        
        # Convert set to list for JSON serialization
        results['ciks_processed'] = list(results['ciks_processed'])
        results['total_ciks'] = len(results['ciks_processed'])
        
        logger.info(f"Demo analysis completed. Processed {results['processed_filings']} filings, "
                   f"analyzed {results['analyzed_filings']} companies")
        
        return results
    
    def generate_csv_summary(self, target_date: date):
        """Generate a CSV summary of all analysis results."""
        if not self.analysis_results:
            logger.warning("No analysis results to summarize")
            return
        
        # Create summary CSV file
        csv_file = self.file_manager.processed_path / f"analysis_summary_{target_date.strftime('%Y%m%d')}.csv"
        
        logger.info(f"Generating CSV summary: {csv_file}")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = [
                'Date',
                'CIK',
                'Company Name',
                'Form Type',
                'Passes Munger Filters',
                'ROE >15% (5yr)',
                'Debt/Equity <8%',
                'Management Ownership >5%',
                'Consistent Growth',
                'Moat Score',
                'Market Share Score',
                'Patent Score', 
                'Customer Retention Score',
                'Pricing Power Score',
                'Base Case Intrinsic Value',
                'Bear Case Intrinsic Value',
                'Bull Case Intrinsic Value',
                'Current Market Price',
                'Margin of Safety %',
                'Investment Attractiveness',
                'Benford Law Score',
                'CAPEX/Depreciation Ratio',
                'True Owner Earnings',
                '5yr Avg ROE %',
                'Debt/Equity Ratio %',
                'Management Ownership %',
                'Business Model Changes',
                'Financial Anomalies',
                'Mental Model Conflicts'
            ]
            writer.writerow(header)
            
            # Write data for each company
            for analysis in self.analysis_results:
                # Get valuation scenarios
                base_case = next((s for s in analysis.valuation_scenarios if s.scenario_name == "Base"), None)
                bear_case = next((s for s in analysis.valuation_scenarios if s.scenario_name == "Bear"), None) 
                bull_case = next((s for s in analysis.valuation_scenarios if s.scenario_name == "Bull"), None)
                
                # Determine investment attractiveness
                if analysis.margin_of_safety is not None:
                    mos_pct = analysis.margin_of_safety * 100
                    if mos_pct > 20:
                        attractiveness = "ATTRACTIVE"
                    elif mos_pct > 0:
                        attractiveness = "FAIR" 
                    else:
                        attractiveness = "OVERVALUED"
                else:
                    attractiveness = "UNKNOWN"
                
                row = [
                    analysis.analysis_date,
                    analysis.cik,
                    analysis.company_name,
                    analysis.form_type,
                    analysis.munger_filters.passes_all_filters,
                    analysis.munger_filters.roe_above_15_for_5_years,
                    analysis.munger_filters.debt_equity_below_8_percent,
                    analysis.munger_filters.management_ownership_above_5_percent,
                    analysis.munger_filters.consistent_earnings_growth,
                    round(analysis.moat_score.total_score, 2),
                    round(analysis.moat_score.market_share_stability, 2),
                    round(analysis.moat_score.patent_portfolio_strength, 2),
                    round(analysis.moat_score.customer_retention_rate, 2),
                    round(analysis.moat_score.pricing_power_evidence, 2),
                    round(base_case.intrinsic_value, 2) if base_case else None,
                    round(bear_case.intrinsic_value, 2) if bear_case else None,
                    round(bull_case.intrinsic_value, 2) if bull_case else None,
                    analysis.current_market_price,
                    round(analysis.margin_of_safety * 100, 1) if analysis.margin_of_safety else None,
                    attractiveness,
                    round(analysis.financial_forensics.benford_law_score, 3),
                    round(analysis.financial_forensics.capex_vs_depreciation_ratio, 2),
                    round(analysis.financial_forensics.true_owner_earnings / 1_000_000, 1),  # In millions
                    round(analysis.financial_forensics.roe_5_year_avg, 1),
                    round(analysis.financial_forensics.debt_equity_ratio, 1),
                    round(analysis.financial_forensics.management_ownership_pct, 1),
                    '; '.join(analysis.business_model_changes) if analysis.business_model_changes else '',
                    '; '.join(analysis.financial_anomalies) if analysis.financial_anomalies else '',
                    '; '.join(analysis.mental_model_conflicts) if analysis.mental_model_conflicts else ''
                ]
                writer.writerow(row)
        
        logger.info(f"CSV summary saved with {len(self.analysis_results)} companies")
        
        # Also create a high-level summary
        self.generate_executive_summary(target_date)
    
    def generate_executive_summary(self, target_date: date):
        """Generate an executive summary markdown file."""
        summary_file = self.file_manager.processed_path / f"executive_summary_{target_date.strftime('%Y%m%d')}.md"
        
        # Calculate summary statistics
        total_companies = len(self.analysis_results)
        passing_munger = sum(1 for a in self.analysis_results if a.munger_filters.passes_all_filters)
        attractive_investments = sum(1 for a in self.analysis_results 
                                   if a.margin_of_safety and a.margin_of_safety > 0.20)
        avg_moat_score = sum(a.moat_score.total_score for a in self.analysis_results) / total_companies
        
        # Find best opportunities
        best_companies = sorted(self.analysis_results, 
                              key=lambda x: (x.munger_filters.passes_all_filters, 
                                           x.margin_of_safety or 0), 
                              reverse=True)[:3]
        
        summary_content = f"""# SEC Filing Analysis - Executive Summary

**Analysis Date:** {target_date}  
**Total Companies Analyzed:** {total_companies}

## Key Findings

### Investment Quality Overview
- **Companies Passing Munger Filters:** {passing_munger}/{total_companies} ({passing_munger/total_companies*100:.1f}%)
- **Attractive Investment Opportunities:** {attractive_investments}/{total_companies} ({attractive_investments/total_companies*100:.1f}%)
- **Average Moat Durability Score:** {avg_moat_score:.1f}/10

### Top Investment Opportunities

"""
        
        for i, company in enumerate(best_companies, 1):
            mos_pct = (company.margin_of_safety * 100) if company.margin_of_safety else 0
            status = "✅ PASSES" if company.munger_filters.passes_all_filters else "❌ FAILS"
            
            summary_content += f"""
#### {i}. {company.company_name} ({company.cik})
- **Munger Filters:** {status}
- **Moat Score:** {company.moat_score.total_score:.1f}/10
- **Margin of Safety:** {mos_pct:.1f}%
- **Form Type:** {company.form_type}
"""
        
        summary_content += f"""

### Analysis Distribution by Filter

| Filter | Passing Companies | Pass Rate |
|--------|------------------|-----------|
| ROE >15% (5 years) | {sum(1 for a in self.analysis_results if a.munger_filters.roe_above_15_for_5_years)} | {sum(1 for a in self.analysis_results if a.munger_filters.roe_above_15_for_5_years)/total_companies*100:.1f}% |
| Debt/Equity <8% | {sum(1 for a in self.analysis_results if a.munger_filters.debt_equity_below_8_percent)} | {sum(1 for a in self.analysis_results if a.munger_filters.debt_equity_below_8_percent)/total_companies*100:.1f}% |
| Management Ownership >5% | {sum(1 for a in self.analysis_results if a.munger_filters.management_ownership_above_5_percent)} | {sum(1 for a in self.analysis_results if a.munger_filters.management_ownership_above_5_percent)/total_companies*100:.1f}% |
| Consistent Growth | {sum(1 for a in self.analysis_results if a.munger_filters.consistent_earnings_growth)} | {sum(1 for a in self.analysis_results if a.munger_filters.consistent_earnings_growth)/total_companies*100:.1f}% |

### Moat Analysis

**Average Scores by Component:**
- Market Share Stability: {sum(a.moat_score.market_share_stability for a in self.analysis_results)/total_companies:.1f}/10
- Patent Portfolio: {sum(a.moat_score.patent_portfolio_strength for a in self.analysis_results)/total_companies:.1f}/10  
- Customer Retention: {sum(a.moat_score.customer_retention_rate for a in self.analysis_results)/total_companies:.1f}/10
- Pricing Power: {sum(a.moat_score.pricing_power_evidence for a in self.analysis_results)/total_companies:.1f}/10

---
*Executive summary generated by SEC Analysis System v2.1 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*

**Files Generated:**
- Individual company analysis: `sec_data/processed/analysis_results/[CIK]/[COMPANY]_[DATE]_munger.md`
- Detailed CSV data: `sec_data/processed/analysis_summary_{target_date.strftime('%Y%m%d')}.csv`
- Company database: `sec_data/processed/company_db.parquet`
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        logger.info(f"Executive summary saved: {summary_file}")
    
    def list_generated_files(self) -> Dict[str, List[str]]:
        """List all files generated by the analysis."""
        files = {
            'markdown_reports': [],
            'json_analyses': [], 
            'csv_summaries': [],
            'databases': []
        }
        
        # Find analysis results
        analysis_path = Path(self.file_manager.analysis_path)
        if analysis_path.exists():
            for cik_dir in analysis_path.iterdir():
                if cik_dir.is_dir():
                    for file in cik_dir.iterdir():
                        if file.suffix == '.md':
                            files['markdown_reports'].append(str(file))
                        elif file.suffix == '.json':
                            files['json_analyses'].append(str(file))
        
        # Find CSV summaries
        processed_path = Path(self.file_manager.processed_path)
        if processed_path.exists():
            for file in processed_path.iterdir():
                if file.suffix == '.csv':
                    files['csv_summaries'].append(str(file))
                elif file.suffix == '.parquet':
                    files['databases'].append(str(file))
        
        return files


def main():
    """Main demo function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Demo SEC Analysis System')
    parser.add_argument('--date', type=str, default='2025-05-30',
                       help='Date to analyze (YYYY-MM-DD)')
    parser.add_argument('--storage-path', type=str, default='sec_data',
                       help='Base storage path')
    parser.add_argument('--max-companies', type=int, default=5,
                       help='Maximum companies to analyze')
    
    args = parser.parse_args()
    
    # Parse target date
    target_date = date.fromisoformat(args.date)
    
    # Run demo
    demo = DemoSECAnalysis(args.storage_path)
    results = demo.run_demo_analysis(target_date, args.max_companies)
    
    # List generated files
    files = demo.list_generated_files()
    
    print(f"\n🎉 Demo analysis completed for {target_date}")
    print(f"📊 Results: {results['analyzed_filings']} companies analyzed")
    print(f"📁 Files generated:")
    print(f"   - Markdown reports: {len(files['markdown_reports'])}")
    print(f"   - JSON analyses: {len(files['json_analyses'])}")
    print(f"   - CSV summaries: {len(files['csv_summaries'])}")
    print(f"   - Databases: {len(files['databases'])}")
    
    if files['csv_summaries']:
        print(f"\n📈 CSV Summary: {files['csv_summaries'][0]}")
    
    if files['markdown_reports']:
        print(f"\n📄 Sample Markdown Report: {files['markdown_reports'][0]}")


if __name__ == "__main__":
    main()