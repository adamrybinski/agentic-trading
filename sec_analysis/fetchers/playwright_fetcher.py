"""
Browser-based SEC data fetcher using Playwright for cases where requests fail.

This fetcher provides a fallback mechanism when direct HTTP requests to SEC.gov
are blocked or fail, using Playwright to simulate a browser.
"""

from typing import Optional
from pathlib import Path
from datetime import date
import logging

logger = logging.getLogger(__name__)


class PlaywrightSECFetcher:
    """
    SEC data fetcher using Playwright as a fallback when requests fail.
    
    This is mentioned in the requirements as an alternative when normal
    API access doesn't work.
    """
    
    def __init__(self):
        """Initialize the Playwright-based fetcher."""
        self.browser = None
        self.page = None
    
    async def setup_browser(self):
        """Setup Playwright browser instance."""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = async_playwright()
            await self.playwright.start()
            
            # Launch browser with proper settings for SEC.gov
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            # Create context with realistic browser settings
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            self.page = await self.context.new_page()
            
            logger.info("Playwright browser setup completed")
            
        except ImportError:
            logger.error("Playwright not installed. Install with: pip install playwright")
            raise
        except Exception as e:
            logger.error(f"Failed to setup Playwright browser: {e}")
            raise
    
    async def download_master_index_browser(self, target_date: date) -> Optional[str]:
        """
        Download master index using browser automation.
        
        Args:
            target_date: The date to download filings for
            
        Returns:
            Content of the master index file as string, or None if failed
        """
        if not self.page:
            await self.setup_browser()
        
        try:
            year = target_date.year
            quarter = (target_date.month - 1) // 3 + 1
            date_str = target_date.strftime("%Y%m%d")
            
            url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR{quarter}/master.{date_str}.idx"
            
            logger.info(f"Downloading master index via browser from: {url}")
            
            # Navigate to the URL
            response = await self.page.goto(url, wait_until='networkidle')
            
            if response.status == 200:
                # Get the page content
                content = await self.page.content()
                
                # Extract text content from the pre-formatted text
                text_content = await self.page.evaluate("""
                    () => {
                        const preElement = document.querySelector('pre');
                        return preElement ? preElement.textContent : document.body.textContent;
                    }
                """)
                
                logger.info(f"Successfully downloaded master index via browser ({len(text_content)} chars)")
                return text_content
            else:
                logger.error(f"Failed to download master index: HTTP {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"Browser-based download failed: {e}")
            return None
    
    async def download_filing_browser(self, filing_url: str) -> Optional[str]:
        """
        Download a filing using browser automation.
        
        Args:
            filing_url: URL of the filing to download
            
        Returns:
            Content of the filing as string, or None if failed
        """
        if not self.page:
            await self.setup_browser()
        
        try:
            logger.info(f"Downloading filing via browser from: {filing_url}")
            
            response = await self.page.goto(filing_url, wait_until='networkidle')
            
            if response.status == 200:
                content = await self.page.content()
                
                # Extract text content
                text_content = await self.page.evaluate("""
                    () => {
                        const preElement = document.querySelector('pre');
                        return preElement ? preElement.textContent : document.body.textContent;
                    }
                """)
                
                logger.info(f"Successfully downloaded filing via browser ({len(text_content)} chars)")
                return text_content
            else:
                logger.error(f"Failed to download filing: HTTP {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"Browser-based filing download failed: {e}")
            return None
    
    async def cleanup(self):
        """Cleanup browser resources."""
        try:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("Browser cleanup completed")
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")


# Example usage demonstrating the fallback mechanism
async def example_usage():
    """Example of how to use the Playwright fallback fetcher."""
    
    # First try regular requests-based fetcher
    from sec_analysis.fetchers import SECFetcher
    
    regular_fetcher = SECFetcher()
    target_date = date(2024, 1, 15)
    
    try:
        # Try normal HTTP request first
        content = regular_fetcher.download_master_index(target_date)
        logger.info("Successfully downloaded using regular HTTP requests")
        return content
        
    except Exception as e:
        logger.warning(f"Regular fetcher failed: {e}. Trying browser fallback...")
        
        # Fallback to browser-based fetching
        browser_fetcher = PlaywrightSECFetcher()
        try:
            content = await browser_fetcher.download_master_index_browser(target_date)
            return content
        finally:
            await browser_fetcher.cleanup()


if __name__ == "__main__":
    import asyncio
    
    async def test_browser_fetcher():
        """Test the browser fetcher independently."""
        fetcher = PlaywrightSECFetcher()
        
        try:
            # Test with a recent date (may not exist, but tests the mechanism)
            test_date = date(2024, 1, 15)
            content = await fetcher.download_master_index_browser(test_date)
            
            if content:
                print(f"Downloaded {len(content)} characters")
                print("First 200 characters:", content[:200])
            else:
                print("No content downloaded")
                
        finally:
            await fetcher.cleanup()
    
    # Uncomment to test (requires playwright installation)
    # asyncio.run(test_browser_fetcher())