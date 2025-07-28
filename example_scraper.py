#!/usr/bin/env python3
"""
Example custom scraper implementations for specific deal websites.
Demonstrates how to integrate custom scraping logic with the notification system.
"""

import re
import requests
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import trafilatura
from bs4 import BeautifulSoup

from web_scraper_integration import DealScraper
from config_manager import ConfigManager

class CustomDealScrapers:
    """Collection of custom scrapers for specific deal websites."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_hotukdeals(self, base_url: str = "https://www.hotukdeals.com/") -> List[Dict[str, Any]]:
        """
        Scrape deals from HotUKDeals website.
        
        Args:
            base_url: Base URL for HotUKDeals
            
        Returns:
            List of deal dictionaries
        """
        deals = []
        
        try:
            # Get the main page content
            content = trafilatura.fetch_url(base_url)
            if not content:
                self.logger.error(f"Failed to fetch content from {base_url}")
                return deals
            
            # Parse with BeautifulSoup for more precise extraction
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for deal containers (adjust selectors based on actual site structure)
            deal_elements = soup.find_all('article', class_=re.compile(r'deal|thread'))
            
            for element in deal_elements[:10]:  # Limit to first 10 deals
                try:
                    # Extract title
                    title_elem = element.find(['h1', 'h2', 'h3'], class_=re.compile(r'title|heading'))
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # Extract URL
                    link_elem = element.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    url = urljoin(base_url, link_elem['href'])
                    
                    # Extract price
                    price = None
                    price_elem = element.find(['span', 'div'], class_=re.compile(r'price|cost'))
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        price_match = re.search(r'[£$€¥₹]\d+[\.,]?\d*', price_text)
                        if price_match:
                            price = price_match.group(0)
                    
                    # Extract description
                    desc_elem = element.find(['p', 'div'], class_=re.compile(r'description|summary'))
                    description = desc_elem.get_text(strip=True)[:200] if desc_elem else None
                    
                    deal = {
                        'title': title,
                        'url': url,
                        'price': price,
                        'description': description,
                        'source': 'HotUKDeals'
                    }
                    
                    deals.append(deal)
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing deal element: {e}")
                    continue
            
            self.logger.info(f"Extracted {len(deals)} deals from HotUKDeals")
            
        except Exception as e:
            self.logger.error(f"Error scraping HotUKDeals: {e}")
        
        return deals
    
    def scrape_dealabs(self, base_url: str = "https://www.dealabs.com/") -> List[Dict[str, Any]]:
        """
        Scrape deals from Dealabs website.
        
        Args:
            base_url: Base URL for Dealabs
            
        Returns:
            List of deal dictionaries
        """
        deals = []
        
        try:
            content = trafilatura.fetch_url(base_url)
            if not content:
                return deals
            
            # Extract deals using trafilatura text content
            text_content = trafilatura.extract(content)
            if not text_content:
                return deals
            
            # Simple pattern matching for deals
            lines = text_content.split('\n')
            current_deal = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for price patterns
                price_match = re.search(r'([£$€¥₹]\d+[\.,]?\d*)', line)
                if price_match and len(line) < 100:  # Likely a price line
                    if current_deal and 'price' not in current_deal:
                        current_deal['price'] = price_match.group(1)
                
                # Look for URLs
                url_match = re.search(r'https?://[^\s]+', line)
                if url_match:
                    if current_deal and 'url' not in current_deal:
                        current_deal['url'] = url_match.group(0)
                
                # Look for deal titles (lines with common deal keywords)
                deal_keywords = ['deal', 'offer', 'sale', 'discount', 'off', 'promo']
                if any(keyword in line.lower() for keyword in deal_keywords) and len(line) > 10:
                    if current_deal:
                        # Finalize previous deal
                        if 'title' in current_deal and 'url' in current_deal:
                            current_deal.setdefault('source', 'Dealabs')
                            deals.append(current_deal)
                    
                    # Start new deal
                    current_deal = {
                        'title': line[:100],
                        'description': line
                    }
            
            # Don't forget the last deal
            if current_deal and 'title' in current_deal and 'url' in current_deal:
                current_deal.setdefault('source', 'Dealabs')
                deals.append(current_deal)
            
            self.logger.info(f"Extracted {len(deals)} deals from Dealabs")
            
        except Exception as e:
            self.logger.error(f"Error scraping Dealabs: {e}")
        
        return deals
    
    def scrape_reddit_deals(self, subreddit: str = "deals") -> List[Dict[str, Any]]:
        """
        Scrape deals from Reddit deal subreddits.
        
        Args:
            subreddit: Subreddit name (without r/)
            
        Returns:
            List of deal dictionaries
        """
        deals = []
        
        try:
            # Use Reddit's JSON API
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=20"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            for post_data in posts:
                try:
                    post = post_data.get('data', {})
                    
                    title = post.get('title', '').strip()
                    if not title:
                        continue
                    
                    # Get the URL - prefer the actual deal URL over Reddit URL
                    url = post.get('url', '')
                    if not url or 'reddit.com' in url:
                        url = f"https://reddit.com{post.get('permalink', '')}"
                    
                    # Extract price from title
                    price = None
                    price_match = re.search(r'[£$€¥₹]\d+[\.,]?\d*', title)
                    if price_match:
                        price = price_match.group(0)
                    
                    # Use post text as description
                    description = post.get('selftext', '')[:200] if post.get('selftext') else None
                    
                    deal = {
                        'title': title,
                        'url': url,
                        'price': price,
                        'description': description,
                        'source': f'Reddit r/{subreddit}',
                        'score': post.get('score', 0)
                    }
                    
                    deals.append(deal)
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing Reddit post: {e}")
                    continue
            
            # Sort by score (upvotes)
            deals.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            self.logger.info(f"Extracted {len(deals)} deals from Reddit r/{subreddit}")
            
        except Exception as e:
            self.logger.error(f"Error scraping Reddit r/{subreddit}: {e}")
        
        return deals

def custom_scraper_function(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Custom scraper function that can be used with the DealScraper.
    
    Args:
        urls: List of URLs to scrape
        
    Returns:
        List of all deals found across all URLs
    """
    scraper = CustomDealScrapers()
    all_deals = []
    
    for url in urls:
        domain = urlparse(url).netloc.lower()
        
        if 'hotukdeals' in domain:
            deals = scraper.scrape_hotukdeals(url)
        elif 'dealabs' in domain:
            deals = scraper.scrape_dealabs(url)
        elif 'reddit.com' in domain and '/r/' in url:
            # Extract subreddit name
            subreddit_match = re.search(r'/r/([^/]+)', url)
            if subreddit_match:
                subreddit = subreddit_match.group(1)
                deals = scraper.scrape_reddit_deals(subreddit)
            else:
                deals = []
        else:
            # Use generic scraping for other sites
            config_manager = ConfigManager()
            deal_scraper = DealScraper(config_manager)
            deals = deal_scraper.scrape_website_for_deals(url)
        
        all_deals.extend(deals)
    
    return all_deals

def main():
    """Example usage of custom scrapers."""
    # Example URLs to scrape
    example_urls = [
        "https://www.hotukdeals.com/",
        "https://www.reddit.com/r/deals",
        "https://www.reddit.com/r/GameDeals"
    ]
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize config and scraper
    config_manager = ConfigManager()
    config_manager.setup_logging()
    
    scraper = DealScraper(config_manager)
    
    print("Running custom scraper example...")
    
    # Run continuous scraping with custom scraper function
    try:
        scraper.run_continuous_scraping(example_urls, custom_scraper_function)
    except KeyboardInterrupt:
        print("\nScraping stopped by user")

if __name__ == "__main__":
    main()
