#!/usr/bin/env python3
"""
Generate comprehensive reports from SEC filing analysis.
Creates individual Markdown reports for each company and CSV summaries.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import date, datetime
import logging
from typing import List, Dict, Any
import os

from sec_analysis.storage import FileManager
from sec_analysis.analyzers import MungerAnalyzer
from sec_analysis.models import Filing, AnalysisResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates comprehensive reports from SEC analysis data."""
    
    def __init__(self, base_storage_path: str = "sec_data"):
        """Initialize the report generator."""
        self.file_manager = FileManager(base_storage_path)
        self.analyzer = MungerAnalyzer()
        
    def load_filings_from_date(self, target_date: date) -> List[Filing]:
        """Load all filings processed for a specific date."""
        try:
            # Load company database
            company_db_path = Path(self.file_manager.base_path) / "processed" / "company_db.parquet"
            if company_db_path.exists():
                company_df = pd.read_parquet(company_db_path)
                logger.info(f"Loaded {len(company_df)} companies from database")
                
                # Convert to Filing objects for the target date
                filings = []
                for _, row in company_df.iterrows():
                    try:
                        filing = Filing(
                            cik=row['cik'],
                            company_name=row['company_name'],
                            form_type=row.get('latest_form_type', '8-K'),
                            date_filed=target_date.strftime('%Y-%m-%d'),
                            url=f"https://www.sec.gov/Archives/{row.get('latest_filename', '')}"
                        )
                        filings.append(filing)
                    except Exception as e:
                        logger.warning(f"Failed to create filing for {row.get('cik', 'unknown')}: {e}")
                        continue
                
                return filings
            else:
                logger.warning("Company database not found")
                return []
                
        except Exception as e:
            logger.error(f"Failed to load filings: {e}")
            return []
    
    def generate_comprehensive_analysis(self, target_date: date, max_companies: int = 50):
        """Generate comprehensive analysis for a specific date."""
        logger.info(f"Generating comprehensive analysis for {target_date}")
        
        # Load filings
        filings = self.load_filings_from_date(target_date)
        if not filings:
            logger.error("No filings found to analyze")
            return
        
        # Limit to max_companies for demo
        filings = filings[:max_companies]
        logger.info(f"Analyzing {len(filings)} companies")
        
        # Generate analysis results
        analysis_results = []
        processed_count = 0
        
        for i, filing in enumerate(filings):
            try:
                logger.info(f"Analyzing {filing.company_name} ({i+1}/{len(filings)})")
                
                # Generate mock financial data for demonstration
                mock_content = self._generate_mock_filing_content(filing)
                
                # Perform Munger analysis
                analysis_result = self.analyzer.analyze_company(
                    filing, mock_content, market_price=None
                )
                
                analysis_results.append(analysis_result)
                processed_count += 1
                
                # Generate individual MD report
                self._generate_company_markdown_report(analysis_result, target_date)
                
            except Exception as e:
                logger.error(f"Failed to analyze {filing.company_name}: {e}")
                continue
        
        # Generate CSV summary
        self._generate_csv_summary(analysis_results, target_date)
        
        # Generate executive summary
        self._generate_executive_summary(analysis_results, target_date)
        
        logger.info(f"Report generation complete. Processed {processed_count} companies.")
    
    def _generate_mock_filing_content(self, filing: Filing) -> str:
        """Generate realistic mock filing content for demonstration."""
        return f"""
UNITED STATES
SECURITIES AND EXCHANGE COMMISSION

FORM 8-K

{filing.company_name}
(Exact name of registrant as specified in its charter)

CIK: {filing.cik}
Date Filed: {filing.date_filed}

FINANCIAL STATEMENTS

Net Income: $2,500,000,000
Revenue: $15,000,000,000
Total Assets: $45,000,000,000
Total Debt: $8,000,000,000
Shareholders' Equity: $25,000,000,000
Cash Flow from Operations: $3,200,000,000
Capital Expenditures: $1,800,000,000
Depreciation: $1,200,000,000

MANAGEMENT'S DISCUSSION AND ANALYSIS

The company has demonstrated consistent growth in revenue and profitability over the past five years.
Our market position remains strong with increasing market share and customer retention.
We continue to invest in research and development to maintain our competitive advantages.
Our patent portfolio has been expanded with 15 new patents filed this year.
Customer retention rate remains above 95% in our core segments.

BUSINESS OPERATIONS

The company operates in highly competitive markets but maintains strong pricing power
due to our differentiated products and services. We have seen consistent demand
across all business segments with particular strength in our core markets.
"""
    
    def _generate_company_markdown_report(self, analysis_result: AnalysisResult, target_date: date):
        """Generate individual markdown report for a company."""
        try:
            # Create directory structure
            reports_dir = Path(self.file_manager.base_path) / "processed" / "analysis_results" / analysis_result.cik
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            company_name_clean = analysis_result.company_name.replace(' ', '_').replace(',', '').replace('.', '')
            filename = f"{company_name_clean}_{target_date.strftime('%Y%m%d')}_munger_analysis.md"
            filepath = reports_dir / filename
            
            # Generate markdown content
            content = self._create_markdown_content(analysis_result)
            
            # Write file
            filepath.write_text(content)
            logger.info(f"Generated markdown report: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to generate markdown report for {analysis_result.company_name}: {e}")
    
    def _create_markdown_content(self, analysis: AnalysisResult) -> str:
        """Create markdown content for a company analysis."""
        # Determine overall assessment
        passes_filters = analysis.munger_filters.passes_all_filters
        status_emoji = "✅" if passes_filters else "❌"
        assessment = "PASSES Munger Filters" if passes_filters else "FAILS Munger Filters"
        
        # Margin of safety assessment
        margin = analysis.margin_of_safety
        if margin > 0.20:
            margin_status = "🟢 **ATTRACTIVE**"
        elif margin > 0.10:
            margin_status = "🟡 **ACCEPTABLE**"
        else:
            margin_status = "🔴 **UNATTRACTIVE**"
        
        # Create content
        content = f"""# {analysis.company_name} - Charlie Munger Investment Analysis

**CIK:** {analysis.cik}  
**Analysis Date:** {analysis.analysis_date}  
**Form Type:** {analysis.form_type}

## {status_emoji} **Overall Assessment: {assessment}**

---

## 🛡️ **Munger Filter Results**

### Four Key Filters:
- **ROE >15% for 5 years:** {'✅ PASS' if analysis.munger_filters.roe_above_15_for_5_years else '❌ FAIL'}
- **Low Debt/Equity (<50%):** {'✅ PASS' if analysis.munger_filters.low_debt_to_equity else '❌ FAIL'}  
- **Consistent Earnings Growth:** {'✅ PASS' if analysis.munger_filters.consistent_earnings_growth else '❌ FAIL'}
- **Strong Free Cash Flow:** {'✅ PASS' if analysis.munger_filters.strong_free_cash_flow else '❌ FAIL'}

---

## 🏰 **Moat Durability Score: {analysis.moat_score:.1f}/10**

### Detailed Breakdown:
- **Market Share Stability (40%):** {analysis.moat_components.market_share_score:.1f}/10
- **Patent Portfolio Strength (30%):** {analysis.moat_components.patent_score:.1f}/10  
- **Customer Retention Rate (20%):** {analysis.moat_components.customer_retention_score:.1f}/10
- **Pricing Power Evidence (10%):** {analysis.moat_components.pricing_power_score:.1f}/10

---

## 💰 **Valuation Analysis**

### **Margin of Safety: {margin:.1%} {margin_status}**

### Three Scenario DCF Analysis:

#### 🐻 **Bear Case**
- **Discount Rate:** 10%
- **Terminal Growth:** 1%
- **Intrinsic Value:** ${analysis.valuation_scenarios[0].intrinsic_value:,.0f}
- **Margin of Safety:** {analysis.valuation_scenarios[0].margin_of_safety:.1%}

#### 📊 **Base Case**  
- **Discount Rate:** 8%
- **Terminal Growth:** 2%
- **Intrinsic Value:** ${analysis.valuation_scenarios[1].intrinsic_value:,.0f}
- **Margin of Safety:** {analysis.valuation_scenarios[1].margin_of_safety:.1%}

#### 🚀 **Bull Case**
- **Discount Rate:** 6%
- **Terminal Growth:** 3%  
- **Intrinsic Value:** ${analysis.valuation_scenarios[2].intrinsic_value:,.0f}
- **Margin of Safety:** {analysis.valuation_scenarios[2].margin_of_safety:.1%}

---

## 🔍 **Financial Forensics**

### Benford's Law Analysis
- **First Digit Distribution:** {'🟢 NORMAL' if analysis.forensics.benfords_law_score > 7 else '🟡 SUSPICIOUS' if analysis.forensics.benfords_law_score > 4 else '🔴 ANOMALOUS'}
- **Score:** {analysis.forensics.benfords_law_score}/10

### Reality Checks
- **CAPEX vs Depreciation:** {'🟢 HEALTHY' if analysis.forensics.capex_vs_depreciation_ratio < 2.0 else '🟡 MONITOR' if analysis.forensics.capex_vs_depreciation_ratio < 3.0 else '🔴 CONCERNING'}
- **Ratio:** {analysis.forensics.capex_vs_depreciation_ratio:.1f}x

### True Owner Earnings
**${analysis.forensics.true_owner_earnings:,.0f}**  
*(Net Income + Depreciation - Maintenance CAPEX)*

---

## 📈 **Business Model Assessment**

### Change Detection
- **Business Model Shifts:** {'⚠️ DETECTED' if analysis.business_model_changes else '✅ STABLE'}
- **MD&A Sentiment:** {analysis.mda_sentiment}

---

## 🧠 **Mental Models Applied**

### Key Insights:
- **Circle of Competence:** Technology sector analysis
- **Inversion:** Risk assessment through failure modes
- **Second-Order Effects:** Market dynamics impact
- **Opportunity Cost:** Relative attractiveness vs alternatives

---

## 🎯 **Investment Recommendation**

### Summary:
Based on Charlie Munger's investment framework, this company {'meets' if passes_filters else 'does not meet'} our stringent criteria for long-term value investing. The {'attractive' if margin > 0.15 else 'limited' if margin > 0.05 else 'inadequate'} margin of safety {'provides' if margin > 0.15 else 'suggests caution in'} investment opportunity.

### Key Strengths:
{self._generate_strengths(analysis)}

### Key Concerns:
{self._generate_concerns(analysis)}

---

*This analysis was generated using Charlie Munger's investment framework focusing on high-quality businesses with durable competitive advantages, purchased at attractive prices with sufficient margin of safety.*
"""
        
        return content
    
    def _generate_strengths(self, analysis: AnalysisResult) -> str:
        """Generate key strengths text."""
        strengths = []
        if analysis.munger_filters.roe_above_15_for_5_years:
            strengths.append("- Strong and consistent return on equity >15%")
        if analysis.munger_filters.low_debt_to_equity:
            strengths.append("- Conservative debt management")
        if analysis.munger_filters.consistent_earnings_growth:
            strengths.append("- Predictable earnings growth pattern")
        if analysis.moat_score > 7:
            strengths.append("- Strong competitive moat with durable advantages")
        if analysis.margin_of_safety > 0.15:
            strengths.append("- Attractive valuation with significant margin of safety")
        
        return "\n".join(strengths) if strengths else "- Limited identifiable strengths based on current analysis"
    
    def _generate_concerns(self, analysis: AnalysisResult) -> str:
        """Generate key concerns text."""
        concerns = []
        if not analysis.munger_filters.roe_above_15_for_5_years:
            concerns.append("- ROE below Munger's 15% threshold")
        if not analysis.munger_filters.low_debt_to_equity:
            concerns.append("- High debt levels create financial risk")
        if not analysis.munger_filters.consistent_earnings_growth:
            concerns.append("- Inconsistent or declining earnings trend")
        if analysis.moat_score < 5:
            concerns.append("- Weak competitive positioning and moat")
        if analysis.margin_of_safety < 0.10:
            concerns.append("- Limited margin of safety at current prices")
        if analysis.forensics.benfords_law_score < 5:
            concerns.append("- Potential accounting irregularities detected")
        
        return "\n".join(concerns) if concerns else "- No major concerns identified in current analysis"
    
    def _generate_csv_summary(self, analysis_results: List[AnalysisResult], target_date: date):
        """Generate CSV summary of all analyses."""
        try:
            # Create summary data
            summary_data = []
            for analysis in analysis_results:
                summary_data.append({
                    'CIK': analysis.cik,
                    'Company_Name': analysis.company_name,
                    'Analysis_Date': analysis.analysis_date,
                    'Form_Type': analysis.form_type,
                    'Passes_Munger_Filters': analysis.munger_filters.passes_all_filters,
                    'ROE_Above_15_For_5_Years': analysis.munger_filters.roe_above_15_for_5_years,
                    'Low_Debt_To_Equity': analysis.munger_filters.low_debt_to_equity,
                    'Consistent_Earnings_Growth': analysis.munger_filters.consistent_earnings_growth,
                    'Strong_Free_Cash_Flow': analysis.munger_filters.strong_free_cash_flow,
                    'Moat_Score': analysis.moat_score,
                    'Market_Share_Score': analysis.moat_components.market_share_score,
                    'Patent_Score': analysis.moat_components.patent_score,
                    'Customer_Retention_Score': analysis.moat_components.customer_retention_score,
                    'Pricing_Power_Score': analysis.moat_components.pricing_power_score,
                    'Margin_of_Safety': analysis.margin_of_safety,
                    'Bear_Case_Intrinsic_Value': analysis.valuation_scenarios[0].intrinsic_value,
                    'Base_Case_Intrinsic_Value': analysis.valuation_scenarios[1].intrinsic_value,
                    'Bull_Case_Intrinsic_Value': analysis.valuation_scenarios[2].intrinsic_value,
                    'Bear_Case_Margin_Safety': analysis.valuation_scenarios[0].margin_of_safety,
                    'Base_Case_Margin_Safety': analysis.valuation_scenarios[1].margin_of_safety,
                    'Bull_Case_Margin_Safety': analysis.valuation_scenarios[2].margin_of_safety,
                    'Benfords_Law_Score': analysis.forensics.benfords_law_score,
                    'CAPEX_vs_Depreciation_Ratio': analysis.forensics.capex_vs_depreciation_ratio,
                    'True_Owner_Earnings': analysis.forensics.true_owner_earnings,
                    'Business_Model_Changes': analysis.business_model_changes,
                    'MDA_Sentiment': analysis.mda_sentiment
                })
            
            # Create DataFrame and save
            df = pd.DataFrame(summary_data)
            
            # Create output directory
            output_dir = Path(self.file_manager.base_path) / "processed"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save CSV
            csv_filename = f"analysis_summary_{target_date.strftime('%Y%m%d')}.csv"
            csv_path = output_dir / csv_filename
            df.to_csv(csv_path, index=False)
            
            logger.info(f"Generated CSV summary: {csv_path}")
            logger.info(f"Summary contains {len(df)} companies")
            
        except Exception as e:
            logger.error(f"Failed to generate CSV summary: {e}")
    
    def _generate_executive_summary(self, analysis_results: List[AnalysisResult], target_date: date):
        """Generate executive summary markdown report."""
        try:
            # Calculate summary statistics
            total_companies = len(analysis_results)
            passed_filters = sum(1 for a in analysis_results if a.munger_filters.passes_all_filters)
            avg_moat_score = sum(a.moat_score for a in analysis_results) / total_companies if total_companies > 0 else 0
            avg_margin_safety = sum(a.margin_of_safety for a in analysis_results) / total_companies if total_companies > 0 else 0
            
            # Top performers
            top_moat = sorted(analysis_results, key=lambda x: x.moat_score, reverse=True)[:5]
            top_margin = sorted(analysis_results, key=lambda x: x.margin_of_safety, reverse=True)[:5]
            munger_passes = [a for a in analysis_results if a.munger_filters.passes_all_filters]
            
            # Create executive summary content
            content = f"""# Executive Summary - SEC Filing Analysis
## {target_date.strftime('%B %d, %Y')}

---

## 📊 **Overall Market Analysis**

**Total Companies Analyzed:** {total_companies}  
**Munger Filter Pass Rate:** {passed_filters}/{total_companies} ({passed_filters/total_companies*100:.1f}%)  
**Average Moat Score:** {avg_moat_score:.1f}/10  
**Average Margin of Safety:** {avg_margin_safety:.1%}

---

## 🏆 **Top Investment Opportunities**

### Companies Passing All Munger Filters ({len(munger_passes)} companies):
"""
            
            for i, analysis in enumerate(munger_passes[:10], 1):
                content += f"{i}. **{analysis.company_name}** (CIK: {analysis.cik}) - Moat: {analysis.moat_score:.1f}, Margin: {analysis.margin_of_safety:.1%}\n"
            
            content += f"""
### Strongest Competitive Moats:
"""
            for i, analysis in enumerate(top_moat, 1):
                content += f"{i}. **{analysis.company_name}** - Moat Score: {analysis.moat_score:.1f}/10\n"
            
            content += f"""
### Best Margin of Safety:
"""
            for i, analysis in enumerate(top_margin, 1):
                content += f"{i}. **{analysis.company_name}** - Margin: {analysis.margin_of_safety:.1%}\n"
            
            content += f"""
---

## 🔍 **Market Insights**

### Sector Distribution:
- **Technology:** {self._count_sector(analysis_results, 'technology')} companies
- **Financial:** {self._count_sector(analysis_results, 'financial')} companies  
- **Healthcare:** {self._count_sector(analysis_results, 'healthcare')} companies
- **Industrial:** {self._count_sector(analysis_results, 'industrial')} companies
- **Consumer:** {self._count_sector(analysis_results, 'consumer')} companies

### Quality Metrics:
- **High Moat (>7.0):** {sum(1 for a in analysis_results if a.moat_score > 7.0)} companies
- **Attractive Valuation (>15% margin):** {sum(1 for a in analysis_results if a.margin_of_safety > 0.15)} companies
- **Strong ROE (>15%):** {sum(1 for a in analysis_results if a.munger_filters.roe_above_15_for_5_years)} companies
- **Low Debt:** {sum(1 for a in analysis_results if a.munger_filters.low_debt_to_equity)} companies

---

## ⚠️ **Risk Assessment**

### Red Flags Detected:
- **Accounting Anomalies:** {sum(1 for a in analysis_results if a.forensics.benfords_law_score < 5)} companies
- **High CAPEX Concerns:** {sum(1 for a in analysis_results if a.forensics.capex_vs_depreciation_ratio > 3.0)} companies
- **Business Model Changes:** {sum(1 for a in analysis_results if a.business_model_changes)} companies

---

## 📈 **Investment Recommendations**

### Immediate Action:
1. **Deep Dive Analysis** on {len(munger_passes)} companies passing all Munger filters
2. **Monitor** {sum(1 for a in analysis_results if a.moat_score > 6 and not a.munger_filters.passes_all_filters)} high-moat companies for filter improvements
3. **Avoid** {sum(1 for a in analysis_results if a.forensics.benfords_law_score < 4)} companies with significant accounting red flags

### Portfolio Allocation Suggestion:
- **Core Holdings (60%):** Companies passing all filters with >20% margin of safety
- **Growth Positions (25%):** High-moat companies with improving fundamentals  
- **Opportunistic (15%):** Temporarily discounted quality companies

---

*Analysis generated using Charlie Munger's investment framework - focusing on quality, moats, and margin of safety.*
"""
            
            # Save executive summary
            output_dir = Path(self.file_manager.base_path) / "processed"
            summary_path = output_dir / f"executive_summary_{target_date.strftime('%Y%m%d')}.md"
            summary_path.write_text(content)
            
            logger.info(f"Generated executive summary: {summary_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate executive summary: {e}")
    
    def _count_sector(self, analysis_results: List[AnalysisResult], sector: str) -> int:
        """Count companies in a sector (simplified heuristic)."""
        count = 0
        sector_keywords = {
            'technology': ['TECH', 'SOFTWARE', 'COMPUTER', 'MICROSOFT', 'APPLE', 'GOOGLE', 'AMAZON'],
            'financial': ['BANK', 'FINANCIAL', 'INSURANCE', 'CAPITAL', 'FUND'],
            'healthcare': ['HEALTH', 'MEDICAL', 'PHARMA', 'BIO', 'CARE'],
            'industrial': ['MANUFACTURING', 'INDUSTRIAL', 'ENGINEERING', 'CONSTRUCTION'],
            'consumer': ['CONSUMER', 'RETAIL', 'FOOD', 'BEVERAGE', 'RESTAURANT']
        }
        
        keywords = sector_keywords.get(sector, [])
        for analysis in analysis_results:
            if any(keyword in analysis.company_name.upper() for keyword in keywords):
                count += 1
        return count


def main():
    """Main function to generate reports."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate comprehensive SEC analysis reports')
    parser.add_argument('--date', type=str, help='Date to generate reports for (YYYY-MM-DD)', 
                       default='2025-01-30')
    parser.add_argument('--max-companies', type=int, default=50,
                       help='Maximum number of companies to analyze')
    parser.add_argument('--storage-path', type=str, default='sec_data',
                       help='Base storage path for SEC data')
    
    args = parser.parse_args()
    
    # Parse date
    try:
        target_date = date.fromisoformat(args.date)
    except ValueError:
        logger.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD")
        return
    
    # Generate reports
    generator = ReportGenerator(args.storage_path)
    generator.generate_comprehensive_analysis(target_date, args.max_companies)


if __name__ == "__main__":
    main()