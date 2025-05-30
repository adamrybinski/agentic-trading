"""SEC data fetcher for downloading daily master index files."""

import requests
from datetime import date, datetime
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SECFetcher:
    """Handles downloading SEC filing data from official sources."""
    
    BASE_URL = "https://www.sec.gov/Archives/edgar/daily-index"
    
    def __init__(self, user_agent: str = "SEC Analysis Tool 1.0"):
        """Initialize the SEC fetcher with proper headers."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        })
    
    def get_master_index_url(self, target_date: date) -> str:
        """Generate the URL for the master index file for a given date."""
        year = target_date.year
        quarter = (target_date.month - 1) // 3 + 1
        date_str = target_date.strftime("%Y%m%d")
        
        return f"{self.BASE_URL}/{year}/QTR{quarter}/master.{date_str}.idx"
    
    def download_master_index(self, target_date: date, save_path: Optional[Path] = None) -> str:
        """
        Download the master index file for a given date.
        
        Args:
            target_date: The date to download filings for
            save_path: Optional path to save the file. If None, returns content as string.
            
        Returns:
            Content of the master index file as string
            
        Raises:
            requests.RequestException: If download fails
        """
        url = self.get_master_index_url(target_date)
        logger.info(f"Downloading master index from: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            
            if save_path:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Master index saved to: {save_path}")
            
            return content
            
        except requests.RequestException as e:
            logger.error(f"Failed to download master index for {target_date}: {e}")
            raise
    
    def download_filing(self, filing_url: str, save_path: Path) -> bool:
        """
        Download a specific filing document.
        
        Args:
            filing_url: Full URL to the filing
            save_path: Path where to save the filing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading filing from: {filing_url}")
            
            response = self.session.get(filing_url, timeout=30)
            response.raise_for_status()
            
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Determine if this is a binary file (PDF) or text
            content_type = response.headers.get('content-type', '').lower()
            is_binary = 'pdf' in content_type or 'application' in content_type
            
            mode = 'wb' if is_binary else 'w'
            encoding = None if is_binary else 'utf-8'
            content = response.content if is_binary else response.text
            
            with open(save_path, mode, encoding=encoding) as f:
                f.write(content)
            
            logger.info(f"Filing saved to: {save_path}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to download filing from {filing_url}: {e}")
            return False
    
    def check_daily_index_exists(self, target_date: date) -> bool:
        """
        Check if a master index file exists for the given date.
        
        Args:
            target_date: The date to check
            
        Returns:
            True if the index exists, False otherwise
        """
        url = self.get_master_index_url(target_date)
        
        try:
            response = self.session.head(url, timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False