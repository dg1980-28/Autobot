#!/usr/bin/env python3
"""
Deal Notification System - Main Entry Point

A comprehensive system for scraping deals and sending notifications to Telegram.
Supports both one-time scraping and continuous monitoring.
"""

import logging
import argparse
import sys
from typing import List, Dict, Any

from config_manager import ConfigManager
from telegram_notifier import TelegramNotifier, MessageFormat
from deal_validator import DealValidator
from web_scraper_integration import DealScraper

def setup_logging():
    """Setup basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('deal_notifier.log')
        ]
    )

def test_notification_system():
    """Test the notification system with a sample deal."""
    print("Testing notification system...")
    
    # Initialize components
    config_manager = ConfigManager()
    config_manager.setup_logging()
    telegram_config = config_manager.load_telegram_config()
    
    # Create notifier
    notifier = TelegramNotifier(
        bot_token=telegram_config.bot_token,
        channel_id=telegram_config.channel_id,
        format_type=MessageFormat.HTML if telegram_config.format_type == "HTML" else MessageFormat.MARKDOWN
    )
    
    # Test connection
    if not notifier.test_connection():
        print("❌ Telegram connection test failed!")
        return False
    
    print("✅ Telegram connection successful!")
    
    # Test notification
    try:
        response = notifier.send_deal_notification(
            title="Test Deal - LEGO Star Wars AT-AT",
            url="https://example.com/deal",
            price="£42.99",
            description="This is a test notification from the deal scraper system."
        )
        
        if response.get('ok'):
            print("✅ Test notification sent successfully!")
            return True
        else:
            print(f"❌ Test notification failed: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Test notification error: {e}")
        return False

def scrape_single_site(url: str):
    """Scrape a single website for deals."""
    print(f"Scraping deals from: {url}")
    
    config_manager = ConfigManager()
    config_manager.setup_logging()
    
    scraper = DealScraper(config_manager)
    deals = scraper.scrape_website_for_deals(url)
    
    print(f"Found {len(deals)} potential deals")
    
    # Process each deal
    sent_count = 0
    for deal in deals:
        if scraper.process_deal(deal):
            sent_count += 1
    
    print(f"Successfully sent {sent_count} deal notifications")

def run_continuous_monitoring(urls: List[str]):
    """Run continuous monitoring of multiple websites."""
    print(f"Starting continuous monitoring of {len(urls)} websites...")
    
    config_manager = ConfigManager()
    config_manager.setup_logging()
    
    scraper = DealScraper(config_manager)
    
    try:
        scraper.run_continuous_scraping(urls)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Monitoring error: {e}")

def send_custom_notification(title: str, url: str, price: str = None):
    """Send a custom notification."""
    print(f"Sending custom notification: {title}")
    
    config_manager = ConfigManager()
    config_manager.setup_logging()
    telegram_config = config_manager.load_telegram_config()
    
    notifier = TelegramNotifier(
        bot_token=telegram_config.bot_token,
        channel_id=telegram_config.channel_id,
        format_type=MessageFormat.HTML if telegram_config.format_type == "HTML" else MessageFormat.MARKDOWN
    )
    
    try:
        response = notifier.send_deal_notification(title, url, price)
        if response.get('ok'):
            print("✅ Notification sent successfully!")
        else:
            print(f"❌ Notification failed: {response}")
    except Exception as e:
        print(f"❌ Notification error: {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Deal Notification System")
    parser.add_argument(
        'command',
        choices=['test', 'scrape', 'monitor', 'notify'],
        help='Command to execute'
    )
    parser.add_argument(
        '--url',
        help='URL to scrape (for scrape command) or deal URL (for notify command)'
    )
    parser.add_argument(
        '--urls',
        nargs='+',
        help='Multiple URLs to monitor (for monitor command)'
    )
    parser.add_argument(
        '--title',
        help='Deal title (for notify command)'
    )
    parser.add_argument(
        '--price',
        help='Deal price (for notify command)'
    )
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Setup basic logging
    setup_logging()
    
    if args.command == 'test':
        success = test_notification_system()
        sys.exit(0 if success else 1)
        
    elif args.command == 'scrape':
        if not args.url:
            print("Error: --url is required for scrape command")
            sys.exit(1)
        scrape_single_site(args.url)
        
    elif args.command == 'monitor':
        if not args.urls:
            print("Error: --urls is required for monitor command")
            sys.exit(1)
        run_continuous_monitoring(args.urls)
        
    elif args.command == 'notify':
        if not args.title or not args.url:
            print("Error: --title and --url are required for notify command")
            sys.exit(1)
        send_custom_notification(args.title, args.url, args.price)

if __name__ == "__main__":
    main()
