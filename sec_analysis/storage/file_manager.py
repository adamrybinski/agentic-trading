"""File management system for organizing SEC filings by CIK."""

import json
import pandas as pd
from pathlib import Path
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from ..models.filing import Filing, CompanyMetadata
from ..models.analysis import AnalysisResult
import logging

logger = logging.getLogger(__name__)


class FileManager:
    """Manages file organization and storage for SEC analysis system."""
    
    def __init__(self, base_path: str = "sec_data"):
        """Initialize the file manager with base storage path."""
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "raw"
        self.processed_path = self.base_path / "processed"
        self.analysis_path = self.processed_path / "analysis_results"
        
        # Create directory structure
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.base_path,
            self.raw_path,
            self.processed_path,
            self.analysis_path
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_daily_raw_path(self, target_date: date) -> Path:
        """Get the path for storing raw filings for a specific date."""
        return self.raw_path / str(target_date.year) / f"{target_date.month:02d}" / f"{target_date.day:02d}"
    
    def get_cik_directory(self, target_date: date, cik: str) -> Path:
        """Get the directory path for a specific CIK on a given date."""
        daily_path = self.get_daily_raw_path(target_date)
        return daily_path / f"CIK_{cik.zfill(10)}"
    
    def save_master_index(self, target_date: date, content: str) -> Path:
        """Save the master index file for a given date."""
        daily_path = self.get_daily_raw_path(target_date)
        daily_path.mkdir(parents=True, exist_ok=True)
        
        master_file = daily_path / "master.idx"
        with open(master_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Master index saved to: {master_file}")
        return master_file
    
    def save_filing(self, filing: Filing, target_date: date, content: str) -> Path:
        """Save a filing to the appropriate CIK directory."""
        cik_dir = self.get_cik_directory(target_date, filing.cik)
        cik_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename based on form type and date
        date_str = target_date.strftime("%Y%m%d")
        extension = self._get_file_extension(filing.filename)
        filename = f"{filing.form_type}_{date_str}{extension}"
        
        file_path = cik_dir / filename
        
        # Determine if binary or text content
        mode = 'wb' if isinstance(content, bytes) else 'w'
        encoding = None if isinstance(content, bytes) else 'utf-8'
        
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        
        logger.info(f"Filing saved to: {file_path}")
        return file_path
    
    def save_filing_metadata(self, filing: Filing, target_date: date, additional_metadata: Dict[str, Any] = None) -> Path:
        """Save filing metadata as a parquet file."""
        cik_dir = self.get_cik_directory(target_date, filing.cik)
        cik_dir.mkdir(parents=True, exist_ok=True)
        
        # Create metadata dictionary
        metadata = {
            'cik': filing.cik,
            'company_name': filing.company_name,
            'form_type': filing.form_type,
            'date_filed': filing.date_filed.isoformat(),
            'filename': filing.filename,
            'url': filing.url,
            'saved_date': target_date.isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        # Convert to DataFrame and save as parquet
        df = pd.DataFrame([metadata])
        metadata_file = cik_dir / "metadata.parquet"
        df.to_parquet(metadata_file, compression='snappy')
        
        logger.info(f"Metadata saved to: {metadata_file}")
        return metadata_file
    
    def save_analysis_result(self, analysis: AnalysisResult) -> Path:
        """Save analysis result as both JSON and human-readable markdown."""
        # Create analysis directory structure
        analysis_dir = self.analysis_path / analysis.cik
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        date_str = analysis.analysis_date.strftime("%Y%m%d")
        
        # Save JSON result
        json_file = analysis_dir / f"{analysis.company_name.replace(' ', '_')}_{date_str}_analysis.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis.model_dump(), f, indent=2, default=str)
        
        # Save human-readable markdown report
        md_file = analysis_dir / f"{analysis.company_name.replace(' ', '_')}_{date_str}_munger.md"
        self._save_markdown_report(analysis, md_file)
        
        logger.info(f"Analysis saved to: {json_file} and {md_file}")
        return json_file
    
    def _save_markdown_report(self, analysis: AnalysisResult, file_path: Path):
        """Generate and save a human-readable Munger-style analysis report."""
        report = f"""# {analysis.company_name} - Charlie Munger Analysis
        
**Analysis Date:** {analysis.analysis_date}  
**Filing Date:** {analysis.filing_date}  
**Form Type:** {analysis.form_type}  
**CIK:** {analysis.cik}

## Munger's Four Filters Assessment

{'✅' if analysis.munger_filters.passes_all_filters else '❌'} **Overall Assessment: {'PASSES' if analysis.munger_filters.passes_all_filters else 'FAILS'} Munger Filters**

- {'✅' if analysis.munger_filters.roe_above_15_for_5_years else '❌'} ROE >15% for 5 consecutive years
- {'✅' if analysis.munger_filters.debt_equity_below_8_percent else '❌'} Debt/Equity <8%
- {'✅' if analysis.munger_filters.management_ownership_above_5_percent else '❌'} Management ownership >5%
- {'✅' if analysis.munger_filters.consistent_earnings_growth else '❌'} Consistent earnings growth

## Moat Durability Score: {analysis.moat_score.total_score:.1f}/10

- **Market Share Stability:** {analysis.moat_score.market_share_stability}/10 (40% weight)
- **Patent Portfolio Strength:** {analysis.moat_score.patent_portfolio_strength}/10 (30% weight)
- **Customer Retention Rate:** {analysis.moat_score.customer_retention_rate}/10 (20% weight)
- **Pricing Power Evidence:** {analysis.moat_score.pricing_power_evidence}/10 (10% weight)

## Financial Forensics

- **Benford's Law Compliance:** {analysis.financial_forensics.benford_law_score:.2f}
- **CAPEX/Depreciation Ratio:** {analysis.financial_forensics.capex_vs_depreciation_ratio:.2f}
- **True Owner Earnings:** ${analysis.financial_forensics.true_owner_earnings:,.0f}
- **5-Year Average ROE:** {analysis.financial_forensics.roe_5_year_avg:.1f}%
- **Debt/Equity Ratio:** {analysis.financial_forensics.debt_equity_ratio:.1f}%
- **Management Ownership:** {analysis.financial_forensics.management_ownership_pct:.1f}%

## Valuation Analysis

"""
        
        # Add valuation scenarios
        for scenario in analysis.valuation_scenarios:
            report += f"""
### {scenario.scenario_name} Case
- **Discount Rate:** {scenario.discount_rate:.1f}%
- **Terminal Growth:** {scenario.terminal_growth_rate:.1f}%
- **Intrinsic Value:** ${scenario.intrinsic_value:,.2f}
- **DCF Value:** ${scenario.dcf_value:,.2f}
- **Graham Formula:** ${scenario.graham_formula_value:,.2f}
- **Earnings Power Value:** ${scenario.earnings_power_value:,.2f}
"""
        
        # Add margin of safety
        if analysis.margin_of_safety is not None:
            mos_pct = analysis.margin_of_safety * 100
            report += f"""
## Margin of Safety

**Current Market Price:** ${analysis.current_market_price:,.2f}  
**Margin of Safety:** {mos_pct:.1f}%  
{'🟢 **ATTRACTIVE**' if mos_pct > 20 else '🟡 **FAIR**' if mos_pct > 0 else '🔴 **OVERVALUED**'}
"""
        
        # Add business analysis
        if analysis.business_model_changes:
            report += f"""
## Business Model Changes
{chr(10).join(f"- {change}" for change in analysis.business_model_changes)}
"""
        
        if analysis.financial_anomalies:
            report += f"""
## Financial Anomalies  
{chr(10).join(f"- {anomaly}" for anomaly in analysis.financial_anomalies)}
"""
        
        if analysis.mental_model_conflicts:
            report += f"""
## Mental Model Conflicts
{chr(10).join(f"- {conflict}" for conflict in analysis.mental_model_conflicts)}
"""
        
        report += f"""
---
*Analysis generated using SEC Analysis System v{analysis.version} on {analysis.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC*
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def update_company_database(self, filings: List[Filing]) -> Path:
        """Update the master company database with new filings."""
        db_file = self.processed_path / "company_db.parquet"
        
        # Load existing database if it exists
        if db_file.exists():
            existing_df = pd.read_parquet(db_file)
            existing_companies = {row['cik']: row for _, row in existing_df.iterrows()}
        else:
            existing_companies = {}
        
        # Process new filings
        updated_companies = {}
        
        for filing in filings:
            cik = filing.cik
            
            if cik in existing_companies:
                # Update existing company
                company = existing_companies[cik].copy()
                forms = set(company.get('forms', []))
                forms.add(filing.form_type)
                company['forms'] = list(forms)
                company['last_updated'] = datetime.utcnow().isoformat()
            else:
                # Create new company entry
                company = {
                    'cik': cik,
                    'company_name': filing.company_name,
                    'ticker': None,  # To be populated later
                    'forms': [filing.form_type],
                    'first_filed': filing.date_filed.isoformat(),
                    'last_updated': datetime.utcnow().isoformat(),
                    'analysis_version': '2.1'
                }
            
            updated_companies[cik] = company
        
        # Merge with existing companies
        all_companies = {**existing_companies, **updated_companies}
        
        # Convert to DataFrame and save
        df = pd.DataFrame(list(all_companies.values()))
        df.to_parquet(db_file, compression='snappy')
        
        logger.info(f"Company database updated with {len(updated_companies)} companies. Total: {len(all_companies)}")
        return db_file
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        if '.' in filename:
            return '.' + filename.split('.')[-1]
        return '.txt'  # Default extension
    
    def get_analysis_files(self, cik: str) -> List[Path]:
        """Get all analysis files for a specific CIK."""
        cik_analysis_dir = self.analysis_path / cik
        if not cik_analysis_dir.exists():
            return []
        
        return list(cik_analysis_dir.glob("*_analysis.json"))
    
    def load_analysis_result(self, file_path: Path) -> AnalysisResult:
        """Load an analysis result from a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return AnalysisResult.model_validate(data)