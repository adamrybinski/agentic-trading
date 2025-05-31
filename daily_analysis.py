#!/usr/bin/env python3
"""
Daily SEC Analysis Script with LLM Enhancement

This script orchestrates the daily SEC filing analysis workflow:
1. Runs the enhanced SEC analysis for the target date
2. Enhances results with LLM analysis using Charlie Munger framework
3. Generates comprehensive reports with LLM insights
"""

import os
import logging
import asyncio
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_sec_analysis import EnhancedSECAnalyzer
from sec_analysis.models.analysis import AnalysisResult
from github_models_analyzer import GitHubModelsAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DailyAnalysisOrchestrator:
    """Orchestrates daily SEC analysis with LLM enhancement."""
    
    def __init__(self, storage_path: str = "sec_data", reports_path: str = "reports"):
        """Initialize the orchestrator."""
        self.storage_path = storage_path
        self.reports_path = reports_path
        self.analyzer = EnhancedSECAnalyzer(storage_path, reports_path)
        self.llm_analyzer = GitHubModelsAnalyzer()
        
        # Load prompts
        self.system_prompt = self._load_prompt("charlie_munger_system_prompt.txt")
        self.user_prompt_template = self._load_prompt("charlie_munger_user_prompt.txt")
        
        logger.info("Daily Analysis Orchestrator initialized")
    
    def _load_prompt(self, filename: str) -> str:
        """Load prompt from file."""
        prompt_path = Path(__file__).parent / filename
        if prompt_path.exists():
            return prompt_path.read_text()
        else:
            logger.warning(f"Prompt file not found: {filename}")
            return ""
    
    async def run_daily_analysis(self, target_date: date, max_companies: Optional[int] = None) -> Dict[str, Any]:
        """Run the complete daily analysis workflow."""
        logger.info(f"Starting daily analysis for {target_date}")
        
        try:
            # Step 1: Check if analysis already completed
            if self._is_analysis_complete(target_date):
                logger.info(f"Analysis for {target_date} already complete. Using existing results.")
                results = self._get_existing_results(target_date)
            else:
                # Step 2: Run enhanced SEC analysis
                logger.info("Running enhanced SEC analysis...")
                results = await self.analyzer.analyze_all_companies_for_date(target_date, max_companies)
            
            # Step 3: Generate combined report
            logger.info("Generating combined reports...")
            self.analyzer.combine_all_reports(target_date)
            
            # Step 4: Enhance with LLM analysis (if GitHub Models available)
            if self._has_github_models_access():
                logger.info("Enhancing with LLM analysis...")
                await self._enhance_with_llm_analysis(target_date)
            else:
                logger.info("GitHub Models not available, skipping LLM enhancement")
            
            # Step 5: Generate final summary
            summary = self._generate_analysis_summary(target_date, results)
            
            logger.info("Daily analysis completed successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Daily analysis failed: {e}")
            raise
    
    def _is_analysis_complete(self, target_date: date) -> bool:
        """Check if analysis for the date is already complete."""
        # Check for progress file
        progress_file = self.analyzer.get_progress_file_path(target_date)
        if not progress_file.exists():
            return False
        
        # Check for combined report
        date_str = target_date.strftime('%Y%m%d')
        combined_report = Path(self.reports_path) / f"all_reports_{date_str}.md"
        
        return combined_report.exists()
    
    def _get_existing_results(self, target_date: date) -> Dict[str, Any]:
        """Get results from existing analysis."""
        progress_file = self.analyzer.get_progress_file_path(target_date)
        if progress_file.exists():
            progress = self.analyzer.load_progress(target_date)
            return {
                'total_companies': progress.get('total_companies', 0),
                'completed': len(progress.get('completed_ciks', [])),
                'failed': len(progress.get('failed_ciks', [])),
                'new_analyses': 0  # No new analyses when using existing
            }
        
        return {'total_companies': 0, 'completed': 0, 'failed': 0, 'new_analyses': 0}
    
    def _has_github_models_access(self) -> bool:
        """Check if GitHub Models API is available."""
        return self.llm_analyzer.is_available()
    
    async def _enhance_with_llm_analysis(self, target_date: date):
        """Enhance analysis results with LLM insights using GitHub Models."""
        if not self.llm_analyzer.is_available():
            logger.warning("GitHub Models not available, skipping LLM enhancement")
            return
        
        if not self.system_prompt or not self.user_prompt_template:
            logger.warning("Charlie Munger prompts not loaded, skipping LLM enhancement")
            return
        
        logger.info("Starting LLM enhancement of analysis results...")
        
        try:
            # Load analysis results for the date
            analysis_results = self._load_analysis_results(target_date)
            
            enhanced_count = 0
            failed_count = 0
            
            # Enhance each analysis with LLM
            for analysis_result in analysis_results:
                try:
                    enhanced_content = await self.llm_analyzer.enhance_analysis(
                        analysis_result, 
                        self.system_prompt, 
                        self.user_prompt_template
                    )
                    
                    if enhanced_content:
                        # Save enhanced analysis
                        date_str = target_date.strftime('%Y-%m-%d')
                        self.llm_analyzer.save_enhanced_analysis(
                            analysis_result.cik,
                            date_str,
                            enhanced_content,
                            self.reports_path
                        )
                        enhanced_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to enhance analysis for {analysis_result.company_name}: {e}")
                    failed_count += 1
            
            logger.info(f"LLM enhancement complete: {enhanced_count} enhanced, {failed_count} failed")
            
        except Exception as e:
            logger.error(f"LLM enhancement failed: {e}")
    
    def _load_analysis_results(self, target_date: date) -> List[AnalysisResult]:
        """Load analysis results for a date."""
        analysis_results = []
        
        try:
            date_str = target_date.strftime('%Y-%m-%d')
            reports_dir = Path(self.reports_path) / date_str
            
            if not reports_dir.exists():
                logger.warning(f"Reports directory not found: {reports_dir}")
                return analysis_results
            
            # Find all company directories
            for company_dir in reports_dir.iterdir():
                if company_dir.is_dir() and company_dir.name.isdigit():
                    # Look for analysis JSON files
                    json_files = list(company_dir.glob("*_analysis.json"))
                    if json_files:
                        try:
                            json_file = json_files[0]
                            with open(json_file, 'r') as f:
                                analysis_data = json.load(f)
                            
                            # Convert to AnalysisResult object
                            analysis_result = AnalysisResult(**analysis_data)
                            analysis_results.append(analysis_result)
                            
                        except Exception as e:
                            logger.warning(f"Failed to load analysis from {json_file}: {e}")
            
            logger.info(f"Loaded {len(analysis_results)} analysis results for {target_date}")
            
        except Exception as e:
            logger.error(f"Failed to load analysis results: {e}")
        
        return analysis_results
    
    def _generate_analysis_summary(self, target_date: date, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the analysis."""
        return {
            'date': target_date.isoformat(),
            'timestamp': datetime.now().isoformat(),
            'total_companies': results.get('total_companies', 0),
            'successfully_analyzed': results.get('completed', 0),
            'failed_analyses': results.get('failed', 0),
            'new_analyses': results.get('new_analyses', 0),
            'reports_generated': True,
            'llm_enhancement': self._has_github_models_access()
        }


async def main():
    """Main entry point for daily analysis."""
    parser = argparse.ArgumentParser(description='Daily SEC Analysis with LLM Enhancement')
    parser.add_argument('--date', type=str, help='Date to analyze (YYYY-MM-DD)', 
                       default=None)
    parser.add_argument('--max-companies', type=int, default=None,
                       help='Maximum number of companies to analyze')
    parser.add_argument('--storage-path', type=str, default='sec_data',
                       help='Base storage path for SEC data')
    parser.add_argument('--reports-path', type=str, default='reports',
                       help='Path where reports are saved')
    
    args = parser.parse_args()
    
    # Default to yesterday if no date specified
    if args.date:
        try:
            target_date = date.fromisoformat(args.date)
        except ValueError:
            logger.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD")
            return 1
    else:
        target_date = date.today() - timedelta(days=1)
    
    # Initialize orchestrator
    orchestrator = DailyAnalysisOrchestrator(args.storage_path, args.reports_path)
    
    try:
        # Run analysis
        summary = await orchestrator.run_daily_analysis(target_date, args.max_companies)
        
        # Print summary
        print(f"\n🎉 Daily Analysis Complete for {target_date}")
        print(f"📊 Total companies: {summary['total_companies']}")
        print(f"✅ Successfully analyzed: {summary['successfully_analyzed']}")
        print(f"❌ Failed analyses: {summary['failed_analyses']}")
        print(f"🆕 New analyses: {summary['new_analyses']}")
        print(f"📈 LLM enhancement: {'✅' if summary['llm_enhancement'] else '❌'}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Daily analysis failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)