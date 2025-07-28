import trafilatura
import logging
import time
import requests
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import re

from telegram_notifier import TelegramNotifier, MessageFormat
from deal_validator import DealValidator
from config_manager import ConfigManager

class DealScraper:
    """
    Web scraper integration for finding deals and sending notifications.
    Integrates with the Telegram notification system.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.telegram_config = config_manager.load_telegram_config()
        self.scraping_config = config_manager.load_scraping_config()
        
        # Initialize components
        self.notifier = TelegramNotifier(
            bot_token=self.telegram_config.bot_token,
            channel_id=self.telegram_config.channel_id,
            format_type=MessageFormat.HTML if self.telegram_config.format_type == "HTML" else MessageFormat.MARKDOWN
        )
        self.validator = DealValidator()
        self.logger = logging.getLogger(__name__)
        
        # Tracking for duplicate prevention
        self.sent_deals = set()
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.scraping_config.user_agent})
    
    def get_website_text_content(self, url: str) -> str:
        """
        Extract main text content from a website using trafilatura.
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Extracted text content
        """
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                return text or ""
            return ""
        except Exception as e:
            self.logger.error(f"Failed to extract content from {url}: {e}")
            return ""
    
    def extract_deals_from_content(self, content: str, base_url: str) -> List[Dict[str, Any]]:
        """
        Extract deal information from scraped content.
        This is a generic implementation - customize for specific sites.
        
        Args:
            content: Scraped text content
            base_url: Base URL for resolving relative links
            
        Returns:
            List of deal dictionaries
        """
        deals = []
        
        # Simple pattern matching for common deal indicators
        deal_patterns = [
            r'(?i)(deal|offer|sale|discount|off).*?([£$€¥₹]\d+[\.,]?\d*)',
            r'(?i)(was|rrp|originally)\s*([£$€¥₹]\d+[\.,]?\d*).*?now\s*([£$€¥₹]\d+[\.,]?\d*)',
            r'(?i)(\d+%)\s*(off|discount|save)',
        ]
        
        # Split content into lines for processing
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Look for deal indicators
            for pattern in deal_patterns:
                match = re.search(pattern, line)
                if match:
                    # Try to extract more context
                    title = line[:100] if len(line) > 100 else line
                    
                    # Look for URLs in nearby lines
                    url = None
                    for j in range(max(0, i-2), min(len(lines), i+3)):
                        url_match = re.search(r'https?://[^\s]+', lines[j])
                        if url_match:
                            url = url_match.group(0)
                            break
                    
                    if not url:
                        url = base_url  # Fallback to base URL
                    
                    # Extract price if found
                    price_match = re.search(r'[£$€¥₹]\d+[\.,]?\d*', line)
                    price = price_match.group(0) if price_match else None
                    
                    deal = {
                        'title': title,
                        'url': url,
                        'price': price,
                        'description': line,
                        'source': base_url
                    }
                    
                    deals.append(deal)
                    break
        
        return deals
    
    def scrape_website_for_deals(self, url: str) -> List[Dict[str, Any]]:
        """
        Scrape a website for deals.
        
        Args:
            url: Website URL to scrape
            
        Returns:
            List of found deals
        """
        try:
            self.logger.info(f"Scraping deals from: {url}")
            
            # Get website content
            content = self.get_website_text_content(url)
            if not content:
                self.logger.warning(f"No content extracted from {url}")
                return []
            
            # Extract deals from content
            deals = self.extract_deals_from_content(content, url)
            
            self.logger.info(f"Found {len(deals)} potential deals from {url}")
            return deals
            
        except Exception as e:
            self.logger.error(f"Failed to scrape {url}: {e}")
            return []
    
    def process_deal(self, deal: Dict[str, Any]) -> bool:
        """
        Process a single deal: validate and send notification.
        
        Args:
            deal: Deal dictionary
            
        Returns:
            True if deal was processed successfully
        """
        try:
            # Create a unique identifier for the deal
            deal_id = f"{deal.get('title', '')[:50]}_{deal.get('url', '')}"
            
            # Skip if already sent
            if deal_id in self.sent_deals:
                self.logger.debug(f"Deal already sent: {deal_id}")
                return False
            
            # Validate deal data
            validation_result = self.validator.validate_deal(
                title=deal.get('title', ''),
                url=deal.get('url', ''),
                price=deal.get('price'),
                description=deal.get('description')
            )
            
            if not validation_result.is_valid:
                self.logger.warning(f"Deal validation failed: {'; '.join(validation_result.errors)}")
                return False
            
            # Send notification
            response = self.notifier.send_deal_notification(
                title=deal['title'],
                url=deal['url'],
                price=deal.get('price'),
                description=deal.get('description')
            )
            
            if response.get('ok'):
                self.sent_deals.add(deal_id)
                self.logger.info(f"Successfully sent deal notification: {deal['title']}")
                return True
            else:
                self.logger.error(f"Failed to send deal notification: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing deal: {e}")
            return False
    
    def scrape_multiple_sites(self, urls: List[str]) -> Dict[str, Any]:
        """
        Scrape multiple websites concurrently for deals.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            Summary of scraping results
        """
        results = {
            'total_sites': len(urls),
            'successful_scrapes': 0,
            'total_deals_found': 0,
            'deals_sent': 0,
            'errors': []
        }
        
        with ThreadPoolExecutor(max_workers=self.scraping_config.max_concurrent_scrapes) as executor:
            # Submit scraping tasks
            future_to_url = {
                executor.submit(self.scrape_website_for_deals, url): url 
                for url in urls
            }
            
            # Process results as they complete
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    deals = future.result()
                    results['successful_scrapes'] += 1
                    results['total_deals_found'] += len(deals)
                    
                    # Process each deal
                    for deal in deals:
                        if self.process_deal(deal):
                            results['deals_sent'] += 1
                            
                except Exception as e:
                    error_msg = f"Error scraping {url}: {e}"
                    results['errors'].append(error_msg)
                    self.logger.error(error_msg)
        
        return results
    
    def run_continuous_scraping(self, urls: List[str], custom_scraper: Optional[Callable] = None):
        """
        Run continuous scraping of websites at configured intervals.
        
        Args:
            urls: List of URLs to scrape
            custom_scraper: Optional custom scraping function
        """
        self.logger.info(f"Starting continuous scraping of {len(urls)} sites")
        self.logger.info(f"Scraping interval: {self.scraping_config.scrape_interval} seconds")
        
        # Test Telegram connection first
        if not self.notifier.test_connection():
            self.logger.error("Telegram connection test failed - aborting")
            return
        
        try:
            while True:
                start_time = time.time()
                
                if custom_scraper:
                    # Use custom scraper function
                    try:
                        deals = custom_scraper(urls)
                        for deal in deals:
                            self.process_deal(deal)
                    except Exception as e:
                        self.logger.error(f"Custom scraper error: {e}")
                else:
                    # Use built-in scraper
                    results = self.scrape_multiple_sites(urls)
                    self.logger.info(f"Scraping cycle complete: {results}")
                
                # Calculate sleep time
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.scraping_config.scrape_interval - elapsed_time)
                
                if sleep_time > 0:
                    self.logger.info(f"Sleeping for {sleep_time:.1f} seconds until next scrape")
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            self.logger.info("Scraping stopped by user")
        except Exception as e:
            self.logger.error(f"Unexpected error in continuous scraping: {e}")
            raise
