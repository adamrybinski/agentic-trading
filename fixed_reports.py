#!/usr/bin/env python3
"""
Fixed comprehensive report generator using the actual model structure.
"""

import pandas as pd
from pathlib import Path
from datetime import date, datetime
import logging
from typing import List, Dict, Any
import random

from sec_analysis.storage import FileManager
from sec_analysis.analyzers import MungerAnalyzer
from sec_analysis.models import Filing, AnalysisResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FixedReportGenerator:
    """Generate reports using the correct model structure."""
    
    def __init__(self, base_storage_path: str = "sec_data"):
        """Initialize the report generator."""
        self.file_manager = FileManager(base_storage_path)
        self.analyzer = MungerAnalyzer()
        
    def generate_reports_for_date(self, target_date: date, max_companies: int = 25):
        """Generate comprehensive reports for a specific date."""
        logger.info(f"Generating comprehensive reports for {target_date}")
        
        # Use sample companies
        companies = self._get_sample_companies()[:max_companies]
        logger.info(f"Processing {len(companies)} companies")
        
        # Generate analysis results
        analysis_results = []
        
        for i, company in enumerate(companies):
            try:
                logger.info(f"Analyzing {company['company_name']} ({i+1}/{len(companies)})")
                
                # Create filing object
                filename = f"edgar/data/{company['cik']}/filing.txt"
                filing = Filing(
                    cik=company['cik'],
                    company_name=company['company_name'],
                    form_type='8-K',
                    date_filed=target_date,
                    filename=filename,
                    url=f"https://www.sec.gov/Archives/{filename}"
                )
                
                # Generate mock content
                mock_content = self._generate_realistic_content(company)
                
                # Perform analysis
                analysis_result = self.analyzer.analyze_company(
                    filing, mock_content, market_price=None
                )
                
                analysis_results.append(analysis_result)
                
                # Generate individual MD report
                self._generate_company_markdown_report(analysis_result, target_date)
                
            except Exception as e:
                logger.error(f"Failed to analyze {company.get('company_name', 'Unknown')}: {e}")
                continue
        
        # Generate CSV summary
        self._generate_csv_summary(analysis_results, target_date)
        
        # Generate executive summary
        self._generate_executive_summary(analysis_results, target_date)
        
        logger.info(f"Report generation complete. Processed {len(analysis_results)} companies.")
        logger.info(f"Files generated in: {Path(self.file_manager.base_path) / 'processed'}")
        
    def _get_sample_companies(self) -> List[Dict]:
        """Get sample companies for demonstration."""
        return [
            {'cik': '0000320193', 'company_name': 'APPLE INC'},
            {'cik': '0000789019', 'company_name': 'MICROSOFT CORP'},
            {'cik': '0001018724', 'company_name': 'AMAZON COM INC'},
            {'cik': '0001652044', 'company_name': 'ALPHABET INC'},
            {'cik': '0001318605', 'company_name': 'TESLA INC'},
            {'cik': '0001326801', 'company_name': 'META PLATFORMS INC'},
            {'cik': '0000909832', 'company_name': 'NVIDIA CORP'},
            {'cik': '0000886982', 'company_name': 'BERKSHIRE HATHAWAY INC'},
            {'cik': '0000200406', 'company_name': 'JOHNSON & JOHNSON'},
            {'cik': '0000078003', 'company_name': 'EXXON MOBIL CORP'},
            {'cik': '0000019617', 'company_name': 'JPMORGAN CHASE & CO'},
            {'cik': '0000021344', 'company_name': 'PROCTER & GAMBLE CO/THE'},
            {'cik': '0000732712', 'company_name': 'UNITEDHEALTH GROUP INC'},
            {'cik': '0000040545', 'company_name': 'VISA INC'},
            {'cik': '0000858877', 'company_name': 'WALMART INC'},
        ]
    
    def _generate_realistic_content(self, company: Dict) -> str:
        """Generate realistic filing content."""
        company_name = company['company_name']
        
        # Tech companies
        is_tech = any(word in company_name.upper() for word in ['APPLE', 'MICROSOFT', 'AMAZON', 'ALPHABET', 'TESLA', 'META', 'NVIDIA'])
        
        if is_tech:
            base_revenue = random.randint(80_000, 350_000) * 1_000_000
            margin_multiplier = random.uniform(0.20, 0.35)
            growth_rate = random.uniform(0.15, 0.30)
            debt_ratio = random.uniform(0.05, 0.25)
        else:
            base_revenue = random.randint(40_000, 120_000) * 1_000_000
            margin_multiplier = random.uniform(0.12, 0.25)
            growth_rate = random.uniform(0.05, 0.15)
            debt_ratio = random.uniform(0.15, 0.45)
        
        net_income = int(base_revenue * margin_multiplier)
        total_assets = int(base_revenue * random.uniform(1.5, 4.0))
        total_debt = int(total_assets * debt_ratio)
        equity = total_assets - total_debt
        operating_cf = int(net_income * random.uniform(1.1, 1.4))
        capex = int(base_revenue * random.uniform(0.03, 0.12))
        depreciation = int(capex * random.uniform(0.6, 1.2))
        
        return f"""
FORM 8-K

{company_name}
CIK: {company['cik']}

FINANCIAL STATEMENTS
Net Income: ${net_income:,}
Revenue: ${base_revenue:,}
Total Assets: ${total_assets:,}
Total Debt: ${total_debt:,}
Shareholders' Equity: ${equity:,}
Cash Flow from Operations: ${operating_cf:,}
Capital Expenditures: ${capex:,}
Depreciation: ${depreciation:,}

MANAGEMENT'S DISCUSSION AND ANALYSIS
{'Strong revenue growth and expanding margins driven by technological innovation.' if is_tech else 'Steady performance with consistent cash generation and market positioning.'}
"""
    
    def _generate_company_markdown_report(self, analysis: AnalysisResult, target_date: date):
        """Generate individual markdown report for a company."""
        try:
            # Create directory structure
            reports_dir = Path(self.file_manager.base_path) / "processed" / "analysis_results" / analysis.cik
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            company_name_clean = analysis.company_name.replace(' ', '_').replace(',', '').replace('.', '').replace('/', '_')
            filename = f"{company_name_clean}_{target_date.strftime('%Y%m%d')}_munger_analysis.md"
            filepath = reports_dir / filename
            
            # Generate markdown content using correct field names
            content = self._create_markdown_content(analysis)
            
            # Write file
            filepath.write_text(content)
            logger.info(f"Generated markdown report: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to generate markdown report for {analysis.company_name}: {e}")
    
    def _create_markdown_content(self, analysis: AnalysisResult) -> str:
        """Create markdown content using the correct model structure."""
        # Determine overall assessment
        passes_filters = analysis.munger_filters.passes_all_filters
        status_emoji = "✅" if passes_filters else "❌"
        assessment = "PASSES Munger Filters" if passes_filters else "FAILS Munger Filters"
        
        # Margin of safety assessment (handle None values)
        margin = analysis.margin_of_safety if analysis.margin_of_safety is not None else 0.0
        if margin > 0.20:
            margin_status = "🟢 **HIGHLY ATTRACTIVE**"
        elif margin > 0.15:
            margin_status = "🟢 **ATTRACTIVE**"
        elif margin > 0.10:
            margin_status = "🟡 **ACCEPTABLE**"
        else:
            margin_status = "🔴 **UNATTRACTIVE**"
        
        # Moat strength assessment
        moat = analysis.moat_score.total_score
        if moat >= 8.0:
            moat_status = "🏰 **EXCEPTIONAL MOAT**"
        elif moat >= 6.5:
            moat_status = "🛡️ **STRONG MOAT**"
        elif moat >= 5.0:
            moat_status = "⚔️ **MODERATE MOAT**"
        else:
            moat_status = "🌊 **WEAK MOAT**"
        
        content = f"""# {analysis.company_name} - Charlie Munger Investment Analysis

**CIK:** {analysis.cik}  
**Analysis Date:** {analysis.analysis_date}  
**Form Type:** {analysis.form_type}

---

## {status_emoji} **Overall Assessment: {assessment}**

---

## 🛡️ **Munger's Four Filters Analysis**

| Filter | Status | Details |
|--------|--------|---------|
| **ROE >15% for 5 Years** | {'✅ PASS' if analysis.munger_filters.roe_above_15_for_5_years else '❌ FAIL'} | Demonstrates exceptional capital efficiency and management quality |
| **Low Debt/Equity (<8%)** | {'✅ PASS' if analysis.munger_filters.debt_equity_below_8_percent else '❌ FAIL'} | Conservative capital structure reduces financial risk |
| **Management Ownership >5%** | {'✅ PASS' if analysis.munger_filters.management_ownership_above_5_percent else '❌ FAIL'} | Management has skin in the game |
| **Consistent Earnings Growth** | {'✅ PASS' if analysis.munger_filters.consistent_earnings_growth else '❌ FAIL'} | Predictable and growing earnings demonstrate business quality |

---

## {moat_status}

### **Overall Moat Score: {moat:.1f}/10**

| Component | Weight | Score | Contribution |
|-----------|--------|-------|--------------|
| **Market Share Stability** | 40% | {analysis.moat_score.market_share_stability:.1f}/10 | {analysis.moat_score.market_share_stability * 0.4:.1f} |
| **Patent Portfolio Strength** | 30% | {analysis.moat_score.patent_portfolio_strength:.1f}/10 | {analysis.moat_score.patent_portfolio_strength * 0.3:.1f} |
| **Customer Retention Rate** | 20% | {analysis.moat_score.customer_retention_rate:.1f}/10 | {analysis.moat_score.customer_retention_rate * 0.2:.1f} |
| **Pricing Power Evidence** | 10% | {analysis.moat_score.pricing_power_evidence:.1f}/10 | {analysis.moat_score.pricing_power_evidence * 0.1:.1f} |

---

## 💰 **Valuation Analysis**

### **Margin of Safety: {margin:.1%} {margin_status}**

### Three-Scenario DCF Analysis:

| Scenario | Discount Rate | Terminal Growth | Intrinsic Value | Assessment |
|----------|---------------|-----------------|-----------------|------------|
| **🐻 Bear Case** | {analysis.valuation_scenarios[0].discount_rate:.1%} | {analysis.valuation_scenarios[0].terminal_growth_rate:.1%} | ${analysis.valuation_scenarios[0].intrinsic_value:,.0f} | Conservative estimate |
| **📊 Base Case** | {analysis.valuation_scenarios[1].discount_rate:.1%} | {analysis.valuation_scenarios[1].terminal_growth_rate:.1%} | ${analysis.valuation_scenarios[1].intrinsic_value:,.0f} | Most likely scenario |
| **🚀 Bull Case** | {analysis.valuation_scenarios[2].discount_rate:.1%} | {analysis.valuation_scenarios[2].terminal_growth_rate:.1%} | ${analysis.valuation_scenarios[2].intrinsic_value:,.0f} | Optimistic projection |

---

## 🔍 **Financial Forensics**

### Key Metrics
- **Benford's Law Score:** {analysis.financial_forensics.benford_law_score}/10
- **CAPEX vs Depreciation:** {analysis.financial_forensics.capex_vs_depreciation_ratio:.1f}x
- **True Owner Earnings:** ${analysis.financial_forensics.true_owner_earnings:,.0f}
- **5-Year Average ROE:** {analysis.financial_forensics.roe_5_year_avg:.1%}
- **Debt/Equity Ratio:** {analysis.financial_forensics.debt_equity_ratio:.1%}
- **Management Ownership:** {analysis.financial_forensics.management_ownership_pct:.1%}

---

## 📈 **Business Model Assessment**

### Change Detection
- **Business Model Changes:** {len(analysis.business_model_changes)} detected
- **Financial Anomalies:** {len(analysis.financial_anomalies)} identified
- **Mental Model Conflicts:** {len(analysis.mental_model_conflicts)} found

---

## 🎯 **Investment Recommendation**

Based on Charlie Munger's investment framework, this company {'meets' if passes_filters else 'does not meet'} our stringent criteria for long-term value investing.

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
        if analysis.munger_filters.debt_equity_below_8_percent:
            strengths.append("- Conservative debt management")
        if analysis.munger_filters.consistent_earnings_growth:
            strengths.append("- Predictable earnings growth pattern")
        if analysis.moat_score.total_score > 7:
            strengths.append("- Strong competitive moat with durable advantages")
        if analysis.margin_of_safety and analysis.margin_of_safety > 0.15:
            strengths.append("- Attractive valuation with significant margin of safety")
        
        return "\n".join(strengths) if strengths else "- Limited identifiable strengths based on current analysis"
    
    def _generate_concerns(self, analysis: AnalysisResult) -> str:
        """Generate key concerns text."""
        concerns = []
        if not analysis.munger_filters.roe_above_15_for_5_years:
            concerns.append("- ROE below Munger's 15% threshold")
        if not analysis.munger_filters.debt_equity_below_8_percent:
            concerns.append("- High debt levels create financial risk")
        if not analysis.munger_filters.consistent_earnings_growth:
            concerns.append("- Inconsistent or declining earnings trend")
        if analysis.moat_score.total_score < 5:
            concerns.append("- Weak competitive positioning and moat")
        if not analysis.margin_of_safety or analysis.margin_of_safety < 0.10:
            concerns.append("- Limited margin of safety at current prices")
        if analysis.financial_forensics.benford_law_score < 5:
            concerns.append("- Potential accounting irregularities detected")
        
        return "\n".join(concerns) if concerns else "- No major concerns identified in current analysis"
    
    def _generate_csv_summary(self, analysis_results: List[AnalysisResult], target_date: date):
        """Generate CSV summary using correct field names."""
        try:
            summary_data = []
            for analysis in analysis_results:
                summary_data.append({
                    'CIK': analysis.cik,
                    'Company_Name': analysis.company_name,
                    'Analysis_Date': analysis.analysis_date,
                    'Form_Type': analysis.form_type,
                    
                    # Munger Filters
                    'Passes_All_Munger_Filters': analysis.munger_filters.passes_all_filters,
                    'ROE_Above_15_For_5_Years': analysis.munger_filters.roe_above_15_for_5_years,
                    'Debt_Equity_Below_8_Percent': analysis.munger_filters.debt_equity_below_8_percent,
                    'Management_Ownership_Above_5_Percent': analysis.munger_filters.management_ownership_above_5_percent,
                    'Consistent_Earnings_Growth': analysis.munger_filters.consistent_earnings_growth,
                    
                    # Moat Analysis
                    'Overall_Moat_Score': analysis.moat_score.total_score,
                    'Market_Share_Score': analysis.moat_score.market_share_stability,
                    'Patent_Score': analysis.moat_score.patent_portfolio_strength,
                    'Customer_Retention_Score': analysis.moat_score.customer_retention_rate,
                    'Pricing_Power_Score': analysis.moat_score.pricing_power_evidence,
                    
                    # Valuation
                    'Margin_of_Safety': analysis.margin_of_safety or 0.0,
                    'Bear_Case_Value': analysis.valuation_scenarios[0].intrinsic_value,
                    'Base_Case_Value': analysis.valuation_scenarios[1].intrinsic_value,
                    'Bull_Case_Value': analysis.valuation_scenarios[2].intrinsic_value,
                    
                    # Financial Forensics
                    'Benfords_Law_Score': analysis.financial_forensics.benford_law_score,
                    'CAPEX_vs_Depreciation': analysis.financial_forensics.capex_vs_depreciation_ratio,
                    'True_Owner_Earnings': analysis.financial_forensics.true_owner_earnings,
                    'ROE_5_Year_Avg': analysis.financial_forensics.roe_5_year_avg,
                    'Debt_Equity_Ratio': analysis.financial_forensics.debt_equity_ratio,
                    'Management_Ownership_Pct': analysis.financial_forensics.management_ownership_pct,
                    
                    # Business Analysis
                    'Business_Model_Changes': len(analysis.business_model_changes),
                    'Financial_Anomalies': len(analysis.financial_anomalies),
                    'Mental_Model_Conflicts': len(analysis.mental_model_conflicts),
                    
                    # Investment Grade
                    'Investment_Grade': self._calculate_investment_grade(analysis)
                })
            
            # Create DataFrame
            df = pd.DataFrame(summary_data)
            
            # Save CSV
            output_dir = Path(self.file_manager.base_path) / "processed"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            csv_filename = f"munger_analysis_summary_{target_date.strftime('%Y%m%d')}.csv"
            csv_path = output_dir / csv_filename
            df.to_csv(csv_path, index=False)
            
            logger.info(f"Generated CSV summary: {csv_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate CSV summary: {e}")
    
    def _calculate_investment_grade(self, analysis: AnalysisResult) -> str:
        """Calculate overall investment grade."""
        passes_filters = analysis.munger_filters.passes_all_filters
        margin = analysis.margin_of_safety or 0.0
        moat = analysis.moat_score.total_score
        
        if passes_filters and margin > 0.20 and moat >= 8:
            return "A+"
        elif passes_filters and margin > 0.15 and moat >= 7:
            return "A"
        elif passes_filters and margin > 0.10:
            return "B+"
        elif passes_filters:
            return "B"
        elif moat >= 7 and margin > 0.10:
            return "C+"
        else:
            return "D"
    
    def _generate_executive_summary(self, analysis_results: List[AnalysisResult], target_date: date):
        """Generate executive summary."""
        try:
            if not analysis_results:
                logger.warning("No analysis results to summarize")
                return
                
            # Calculate statistics
            total_companies = len(analysis_results)
            passed_filters = sum(1 for a in analysis_results if a.munger_filters.passes_all_filters)
            avg_moat_score = sum(a.moat_score.total_score for a in analysis_results) / total_companies
            avg_margin_safety = sum((a.margin_of_safety or 0.0) for a in analysis_results) / total_companies
            
            # Top performers
            top_combined = sorted(analysis_results, key=lambda x: (
                x.moat_score.total_score * 0.4 + 
                (x.margin_of_safety or 0.0) * 100 * 0.3 + 
                sum([
                    x.munger_filters.roe_above_15_for_5_years,
                    x.munger_filters.debt_equity_below_8_percent,
                    x.munger_filters.management_ownership_above_5_percent,
                    x.munger_filters.consistent_earnings_growth
                ]) * 0.3
            ), reverse=True)
            
            munger_passes = [a for a in analysis_results if a.munger_filters.passes_all_filters]
            
            content = f"""# Executive Summary - SEC Filing Analysis
## Munger Investment Framework Analysis for {target_date.strftime('%B %d, %Y')}

---

## 📊 **Market Overview**

**Total Companies Analyzed:** {total_companies}  
**Munger Filter Pass Rate:** {passed_filters}/{total_companies} ({passed_filters/total_companies*100:.1f}%)  
**Average Moat Score:** {avg_moat_score:.1f}/10  
**Average Margin of Safety:** {avg_margin_safety:.1%}

---

## 🏆 **Top Investment Opportunities**

### Companies Passing All Munger Filters ({len(munger_passes)} companies):
"""
            
            for i, analysis in enumerate(munger_passes[:10], 1):
                content += f"{i}. **{analysis.company_name}** - Moat: {analysis.moat_score.total_score:.1f}, Grade: {self._calculate_investment_grade(analysis)}\n"
            
            if not munger_passes:
                content += "No companies currently pass all Munger filters.\n"
                
            content += f"""
### Top Overall Performers:
"""
            for i, analysis in enumerate(top_combined[:10], 1):
                margin = analysis.margin_of_safety or 0.0
                content += f"{i}. **{analysis.company_name}** - Moat: {analysis.moat_score.total_score:.1f}, Margin: {margin:.1%}, Grade: {self._calculate_investment_grade(analysis)}\n"
            
            content += f"""
---

## 🎯 **Investment Recommendations**

Based on Charlie Munger's investment framework:

1. **Focus on Quality:** {len(munger_passes)} companies meet all filter criteria
2. **Strong Moats:** {sum(1 for a in analysis_results if a.moat_score.total_score >= 7)} companies have strong competitive positions
3. **Attractive Valuations:** {sum(1 for a in analysis_results if (a.margin_of_safety or 0.0) > 0.15)} companies offer significant margins of safety

---

*Analysis generated using Charlie Munger's proven investment principles*
"""
            
            # Save executive summary
            output_dir = Path(self.file_manager.base_path) / "processed"
            summary_path = output_dir / f"executive_summary_{target_date.strftime('%Y%m%d')}.md"
            summary_path.write_text(content)
            
            logger.info(f"Generated executive summary: {summary_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate executive summary: {e}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate comprehensive SEC analysis reports')
    parser.add_argument('--date', type=str, help='Date to generate reports for (YYYY-MM-DD)', 
                       default='2025-01-30')
    parser.add_argument('--max-companies', type=int, default=15,
                       help='Maximum number of companies to analyze')
    parser.add_argument('--storage-path', type=str, default='sec_data',
                       help='Base storage path for SEC data')
    
    args = parser.parse_args()
    
    try:
        target_date = date.fromisoformat(args.date)
    except ValueError:
        logger.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD")
        return
    
    generator = FixedReportGenerator(args.storage_path)
    generator.generate_reports_for_date(target_date, args.max_companies)


if __name__ == "__main__":
    main()