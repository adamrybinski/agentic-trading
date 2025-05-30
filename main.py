"""
Main processing script for the SEC Analysis System.

This script implements the daily filing processing workflow as specified
in the design document.
"""

import logging
import sys
from datetime import date, datetime, timedelta
from typing import List, Optional
from pathlib import Path

from sec_analysis.fetchers import SECFetcher
from sec_analysis.parsers import MasterIndexParser
from sec_analysis.storage import FileManager
from sec_analysis.analyzers import MungerAnalyzer
from sec_analysis.models import Filing, MasterIndexEntry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sec_analysis.log')
    ]
)

logger = logging.getLogger(__name__)


class SECAnalysisProcessor:
    """Main processor for SEC filing analysis workflow."""
    
    def __init__(self, base_storage_path: str = "sec_data"):
        """Initialize the processor with required components."""
        self.fetcher = SECFetcher()
        self.parser = MasterIndexParser()
        self.file_manager = FileManager(base_storage_path)
        self.analyzer = MungerAnalyzer()
        
        logger.info(f"SEC Analysis Processor initialized with storage path: {base_storage_path}")
    
    def process_daily_filings(self, target_date: date, 
                            analyze_filings: bool = True,
                            max_filings_to_analyze: int = 10) -> dict:
        """
        Process all filings for a given date following the design workflow.
        
        Args:
            target_date: The date to process filings for
            analyze_filings: Whether to perform Munger analysis on filings
            max_filings_to_analyze: Maximum number of filings to analyze
            
        Returns:
            Dictionary with processing results and statistics
        """
        logger.info(f"Starting daily filing processing for {target_date}")
        
        try:
            # Step 1: Download master index
            logger.info("Step 1: Downloading master index")
            master_content = self.fetcher.download_master_index(target_date)
            
            # Save master index
            master_file_path = self.file_manager.save_master_index(target_date, master_content)
            
            # Step 2: Parse and filter filings
            logger.info("Step 2: Parsing master index and filtering filings")
            entries = self.parser.parse_master_index(master_content)
            
            # Convert to Filing objects
            filings = [entry.to_filing() for entry in entries]
            
            logger.info(f"Found {len(filings)} relevant filings")
            
            # Step 3: Organize by CIK-Name pair
            logger.info("Step 3: Organizing filings by CIK")
            results = {
                'date': target_date,
                'total_filings': len(filings),
                'processed_filings': 0,
                'analyzed_filings': 0,
                'ciks_processed': set(),
                'errors': []
            }
            
            for filing in filings:
                try:
                    # Save filing metadata
                    self.file_manager.save_filing_metadata(filing, target_date)
                    results['processed_filings'] += 1
                    results['ciks_processed'].add(filing.cik)
                    
                    # Download and save actual filing if analyzing
                    if (analyze_filings and 
                        results['analyzed_filings'] < max_filings_to_analyze):
                        
                        self._process_individual_filing(filing, target_date, results)
                    
                except Exception as e:
                    error_msg = f"Error processing filing {filing.cik}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            # Step 4: Update master registry
            logger.info("Step 4: Updating company database")
            self.file_manager.update_company_database(filings)
            
            # Convert set to list for JSON serialization
            results['ciks_processed'] = list(results['ciks_processed'])
            results['total_ciks'] = len(results['ciks_processed'])
            
            logger.info(f"Daily processing completed. Processed {results['processed_filings']} filings, "
                       f"analyzed {results['analyzed_filings']} filings for {results['total_ciks']} companies")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to process daily filings for {target_date}: {str(e)}")
            raise
    
    def _process_individual_filing(self, filing: Filing, target_date: date, results: dict):
        """Process and analyze an individual filing."""
        try:
            logger.info(f"Downloading and analyzing filing for {filing.company_name} ({filing.form_type})")
            
            # Download filing content
            filing_content = self._download_filing_content(filing)
            
            if filing_content:
                # Save filing content
                self.file_manager.save_filing(filing, target_date, filing_content)
                
                # Perform Munger analysis
                analysis_result = self.analyzer.analyze_company(
                    filing, filing_content, market_price=None
                )
                
                # Save analysis results
                self.file_manager.save_analysis_result(analysis_result)
                
                results['analyzed_filings'] += 1
                logger.info(f"Analysis completed for {filing.company_name}")
            
        except Exception as e:
            error_msg = f"Error analyzing filing {filing.cik}: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
    
    def _download_filing_content(self, filing: Filing) -> Optional[str]:
        """Download the content of a filing."""
        try:
            import requests
            
            response = self.fetcher.session.get(filing.url, timeout=30)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to download filing content from {filing.url}: {e}")
            return None
    
    def process_date_range(self, start_date: date, end_date: date, 
                          skip_weekends: bool = True) -> List[dict]:
        """
        Process filings for a range of dates.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            skip_weekends: Whether to skip weekends
            
        Returns:
            List of processing results for each date
        """
        results = []
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends if requested
            if skip_weekends and current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_date += timedelta(days=1)
                continue
            
            # Check if filing exists for this date
            if self.fetcher.check_daily_index_exists(current_date):
                try:
                    daily_result = self.process_daily_filings(current_date)
                    results.append(daily_result)
                except Exception as e:
                    logger.error(f"Failed to process {current_date}: {e}")
                    results.append({
                        'date': current_date,
                        'error': str(e),
                        'total_filings': 0
                    })
            else:
                logger.info(f"No filings available for {current_date}")
                results.append({
                    'date': current_date,
                    'message': 'No filings available',
                    'total_filings': 0
                })
            
            current_date += timedelta(days=1)
        
        return results
    
    def get_processing_statistics(self, results: List[dict]) -> dict:
        """Generate summary statistics from processing results."""
        total_filings = sum(r.get('total_filings', 0) for r in results)
        total_analyzed = sum(r.get('analyzed_filings', 0) for r in results)
        total_errors = sum(len(r.get('errors', [])) for r in results)
        
        all_ciks = set()
        for r in results:
            all_ciks.update(r.get('ciks_processed', []))
        
        return {
            'total_dates_processed': len(results),
            'total_filings_found': total_filings,
            'total_filings_analyzed': total_analyzed,
            'total_unique_companies': len(all_ciks),
            'total_errors': total_errors,
            'analysis_rate': total_analyzed / total_filings if total_filings > 0 else 0
        }


def main():
    """Main entry point for the SEC analysis system."""
    import argparse
    
    parser = argparse.ArgumentParser(description='SEC Analysis System')
    parser.add_argument('--date', type=str, help='Date to process (YYYY-MM-DD). Default: yesterday')
    parser.add_argument('--start-date', type=str, help='Start date for range processing (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date for range processing (YYYY-MM-DD)')
    parser.add_argument('--storage-path', type=str, default='sec_data', 
                       help='Base storage path for SEC data')
    parser.add_argument('--max-analyze', type=int, default=10,
                       help='Maximum number of filings to analyze per day')
    parser.add_argument('--no-analysis', action='store_true',
                       help='Skip Munger analysis, only download and organize')
    
    args = parser.parse_args()
    
    processor = SECAnalysisProcessor(args.storage_path)
    
    try:
        if args.start_date and args.end_date:
            # Process date range
            start = date.fromisoformat(args.start_date)
            end = date.fromisoformat(args.end_date)
            
            logger.info(f"Processing date range: {start} to {end}")
            results = processor.process_date_range(start, end)
            
            # Print statistics
            stats = processor.get_processing_statistics(results)
            logger.info(f"Processing complete. Statistics: {stats}")
            
        else:
            # Process single date
            if args.date:
                target_date = date.fromisoformat(args.date)
            else:
                # Default to yesterday
                target_date = date.today() - timedelta(days=1)
            
            logger.info(f"Processing single date: {target_date}")
            result = processor.process_daily_filings(
                target_date, 
                analyze_filings=not args.no_analysis,
                max_filings_to_analyze=args.max_analyze
            )
            
            logger.info(f"Processing complete. Result: {result}")
    
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()