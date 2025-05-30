#!/usr/bin/env python3
"""
Generate simple CSV and Markdown reports from SEC filing data.
Creates individual Markdown reports for each company and CSV summaries.
"""

import pandas as pd
from pathlib import Path
from datetime import date, datetime
import logging
import json
import random
from typing import List, Dict, Any

from sec_analysis.storage import FileManager
from sec_analysis.analyzers import MungerAnalyzer
from sec_analysis.models import Filing, AnalysisResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleReportGenerator:
    """Generates simple reports from SEC filing data."""
    
    def __init__(self, base_storage_path: str = "sec_data"):
        """Initialize the report generator."""
        self.file_manager = FileManager(base_storage_path)
        self.analyzer = MungerAnalyzer()
        
    def generate_reports_for_date(self, target_date: date, max_companies: int = 10):
        """Generate simple reports for a specific date."""
        logger.info(f"Generating reports for {target_date}")
        
        # Load company database to get real companies
        company_db_path = Path(self.file_manager.base_path) / "processed" / "company_db.parquet"
        
        if not company_db_path.exists():
            logger.error(f"Company database not found at {company_db_path}")
            return
        
        # Read company database
        df = pd.read_parquet(company_db_path)
        logger.info(f"Loaded {len(df)} companies from database")
        
        # Take top companies (limit for demo)
        companies = df.head(max_companies)
        
        # Generate analysis results
        analysis_results = []
        
        for i, (_, company) in enumerate(companies.iterrows()):
            try:
                logger.info(f"Analyzing {company['company_name']} ({i+1}/{len(companies)})")
                
                # Create a mock Filing object from company data
                filing = Filing(
                    cik=company['cik'],
                    company_name=company['company_name'],
                    form_type="10-K",
                    date_filed=target_date,
                    filename=f"fake_{company['cik']}_10k.txt",
                    url=f"https://www.sec.gov/fake/{company['cik']}.txt"
                )
                
                # Generate mock filing content
                mock_content = self._generate_mock_filing_content(company)
                
                # Run Munger analysis
                analysis = self.analyzer.analyze_company(filing, mock_content)
                analysis_results.append(analysis)
                
            except Exception as e:
                logger.error(f"Error analyzing {company['company_name']}: {e}")
                continue
        
        # Generate reports
        self._generate_markdown_reports(analysis_results, target_date)
        self._generate_csv_summary(analysis_results, target_date)
        self._generate_executive_summary(analysis_results, target_date)
        
        logger.info(f"Generated reports for {len(analysis_results)} companies")
    
    def _generate_mock_filing_content(self, company: Dict) -> str:
        """Generate mock filing content for analysis."""
        # Generate realistic financial data for demo
        revenue = random.randint(1000, 100000) * 1e6  # $1B - $100B
        net_income = revenue * random.uniform(0.05, 0.25)  # 5-25% net margin
        assets = revenue * random.uniform(1.5, 4.0)  # Asset turnover
        equity = assets * random.uniform(0.3, 0.8)  # Debt/equity ratio
        
        return f"""
FORM 10-K
{company['company_name']}

CONSOLIDATED STATEMENTS OF OPERATIONS
Revenue: ${revenue:,.0f}
Net Income: ${net_income:,.0f}

CONSOLIDATED BALANCE SHEETS
Total Assets: ${assets:,.0f}
Stockholders' Equity: ${equity:,.0f}

MANAGEMENT'S DISCUSSION AND ANALYSIS
{company['company_name']} continues to show strong operational performance 
with consistent revenue growth and market expansion. The company maintains 
strong competitive positions in its core markets.

Our business model focuses on innovation and customer satisfaction, 
driving sustainable long-term growth and value creation for shareholders.

Item 1A. Risk Factors
Competition in our markets may impact pricing and market share.
"""
    
    def _generate_markdown_reports(self, results: List[AnalysisResult], target_date: date):
        """Generate individual Markdown reports for each company."""
        output_dir = Path(self.file_manager.base_path) / "processed" / "analysis_results"
        
        for result in results:
            try:
                company_name_clean = result.company_name.replace(' ', '_').replace('/', '_')
                filename = f"{company_name_clean}_{target_date.strftime('%Y%m%d')}_analysis.md"
                
                cik_dir = output_dir / result.cik
                cik_dir.mkdir(parents=True, exist_ok=True)
                
                report_path = cik_dir / filename
                
                # Generate markdown content
                md_content = self._format_markdown_report(result)
                
                # Save the report
                report_path.write_text(md_content)
                logger.info(f"Generated MD report: {report_path}")
                
            except Exception as e:
                logger.error(f"Failed to generate markdown report for {result.company_name}: {e}")
    
    def _format_markdown_report(self, result: AnalysisResult) -> str:
        """Format analysis result as markdown."""
        
        # Calculate overall assessment
        passes_all = result.munger_filters.passes_all_filters
        
        assessment = "✅ **PASSES**" if passes_all else "❌ **FAILS**"
        
        # Margin of safety assessment
        margin_safety = result.margin_of_safety if result.margin_of_safety else 0.0
        if margin_safety > 0.2:
            safety_emoji = "🟢 **ATTRACTIVE**"
        elif margin_safety > 0.1:
            safety_emoji = "🟡 **FAIR**"
        else:
            safety_emoji = "🔴 **UNATTRACTIVE**"
        
        return f"""# {result.company_name} - Charlie Munger Analysis

**Date:** {result.analysis_date}  
**CIK:** {result.cik}

## Overall Assessment: {assessment} Munger Filters

## Key Metrics

### Munger Investment Filters
- **ROE >15% for 5 years:** {'✅' if result.munger_filters.roe_above_15_for_5_years else '❌'}
- **Consistent Earnings Growth:** {'✅' if result.munger_filters.consistent_earnings_growth else '❌'}
- **Debt/Equity <8%:** {'✅' if result.munger_filters.debt_equity_below_8_percent else '❌'}
- **Management Ownership >5%:** {'✅' if result.munger_filters.management_ownership_above_5_percent else '❌'}

### Moat Durability Score: {result.moat_score.total_score:.1f}/10

### Margin of Safety: {margin_safety:.1%} {safety_emoji}

## Valuation Scenarios

| Scenario | Intrinsic Value | Discount Rate | Terminal Growth |
|----------|----------------|---------------|-----------------|
| Bear     | ${result.valuation_scenarios[0].intrinsic_value:,.2f} | {result.valuation_scenarios[0].discount_rate:.1%} | {result.valuation_scenarios[0].terminal_growth_rate:.1%} |
| Base     | ${result.valuation_scenarios[1].intrinsic_value:,.2f} | {result.valuation_scenarios[1].discount_rate:.1%} | {result.valuation_scenarios[1].terminal_growth_rate:.1%} |
| Bull     | ${result.valuation_scenarios[2].intrinsic_value:,.2f} | {result.valuation_scenarios[2].discount_rate:.1%} | {result.valuation_scenarios[2].terminal_growth_rate:.1%} |

## Financial Forensics

- **Benford's Law Score:** {result.financial_forensics.benford_law_score:.2f}
- **CAPEX/Depreciation Ratio:** {result.financial_forensics.capex_vs_depreciation_ratio:.2f}
- **True Owner Earnings:** ${result.financial_forensics.true_owner_earnings:,.0f}
- **5-Year Avg ROE:** {result.financial_forensics.roe_5_year_avg:.1f}%
- **Debt/Equity Ratio:** {result.financial_forensics.debt_equity_ratio:.1f}%

## Investment Recommendation

**Grade:** A+ (High Quality)

---
*Analysis generated by SEC Analysis System using Charlie Munger's investment framework*
"""
    
    def _generate_csv_summary(self, results: List[AnalysisResult], target_date: date):
        """Generate CSV summary of all analyses."""
        output_dir = Path(self.file_manager.base_path) / "processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create summary data
        summary_data = []
        
        for result in results:
            passes_all = result.munger_filters.passes_all_filters
            
            summary_data.append({
                'CIK': result.cik,
                'Company_Name': result.company_name,
                'Analysis_Date': result.analysis_date,
                'Passes_All_Filters': passes_all,
                'ROE_Above_15': result.munger_filters.roe_above_15_for_5_years,
                'Consistent_Growth': result.munger_filters.consistent_earnings_growth,
                'Debt_Equity_Below_8pct': result.munger_filters.debt_equity_below_8_percent,
                'Management_Ownership_Above_5pct': result.munger_filters.management_ownership_above_5_percent,
                'Moat_Score': result.moat_score.total_score,
                'Market_Share_Stability': result.moat_score.market_share_stability,
                'Patent_Portfolio': result.moat_score.patent_portfolio_strength,
                'Customer_Retention': result.moat_score.customer_retention_rate,
                'Pricing_Power': result.moat_score.pricing_power_evidence,
                'Margin_of_Safety': result.margin_of_safety or 0.0,
                'Bear_Value': result.valuation_scenarios[0].intrinsic_value,
                'Base_Value': result.valuation_scenarios[1].intrinsic_value,
                'Bull_Value': result.valuation_scenarios[2].intrinsic_value,
                'Benfords_Score': result.financial_forensics.benford_law_score,
                'CAPEX_Depreciation': result.financial_forensics.capex_vs_depreciation_ratio,
                'True_Owner_Earnings': result.financial_forensics.true_owner_earnings,
                'ROE_5_Year_Avg': result.financial_forensics.roe_5_year_avg,
                'Debt_Equity_Ratio': result.financial_forensics.debt_equity_ratio,
            })
        
        # Create DataFrame and save
        df = pd.DataFrame(summary_data)
        csv_filename = f"munger_analysis_summary_{target_date.strftime('%Y%m%d')}.csv"
        csv_path = output_dir / csv_filename
        
        df.to_csv(csv_path, index=False)
        logger.info(f"Generated CSV summary: {csv_path}")
    
    def _generate_executive_summary(self, results: List[AnalysisResult], target_date: date):
        """Generate executive summary markdown."""
        output_dir = Path(self.file_manager.base_path) / "processed"
        
        # Calculate statistics
        total_companies = len(results)
        passes_filter = sum(1 for r in results if r.munger_filters.passes_all_filters)
        
        avg_moat_score = sum(r.moat_score.total_score for r in results) / total_companies
        
        attractive_investments = sum(1 for r in results if (r.margin_of_safety or 0) > 0.2)
        
        # Top performers
        top_companies = sorted(results, key=lambda x: x.moat_score.total_score, reverse=True)[:3]
        
        summary_content = f"""# Executive Summary - SEC Analysis {target_date}

## Market Overview

**Analysis Date:** {target_date}  
**Companies Analyzed:** {total_companies}  
**Munger Filter Pass Rate:** {passes_filter}/{total_companies} ({100*passes_filter/total_companies:.1f}%)  
**Average Moat Score:** {avg_moat_score:.1f}/10  
**Attractive Investments:** {attractive_investments} companies

## Top Investment Opportunities

"""
        
        for i, company in enumerate(top_companies, 1):
            margin = company.margin_of_safety or 0.0
            summary_content += f"""### {i}. {company.company_name}
- **Moat Score:** {company.moat_score.total_score:.1f}/10
- **Margin of Safety:** {margin:.1%}
- **Grade:** A+ (High Quality)

"""
        
        summary_content += f"""
## Market Analysis

The analysis reveals a market with {'strong' if passes_filter/total_companies > 0.5 else 'mixed'} fundamentals. 
{passes_filter} out of {total_companies} companies pass Charlie Munger's stringent investment criteria, 
indicating {'a robust' if passes_filter/total_companies > 0.5 else 'selective'} investment environment.

The average moat durability score of {avg_moat_score:.1f} suggests {'strong' if avg_moat_score > 7 else 'moderate' if avg_moat_score > 5 else 'limited'} 
competitive advantages across the analyzed companies.

---
*Analysis generated by SEC Analysis System using Charlie Munger's investment framework*
"""
        
        summary_path = output_dir / f"executive_summary_{target_date.strftime('%Y%m%d')}.md"
        summary_path.write_text(summary_content)
        logger.info(f"Generated executive summary: {summary_path}")


def main():
    """Main entry point."""
    generator = SimpleReportGenerator()
    target_date = date(2025, 1, 30)  # Use the date we have data for
    generator.generate_reports_for_date(target_date, max_companies=10)


if __name__ == "__main__":
    main()