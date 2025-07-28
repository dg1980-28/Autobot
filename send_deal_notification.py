#!/usr/bin/env python3
"""
Simple deal notification function for integration with existing web scrapers.
This function can be called from your scraper whenever a new deal is found.
"""

import requests
import logging
from typing import Optional, Dict, Any

# Configure these values or use environment variables
import os
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8221917763:AAGGzoTtDPmgdo4etyNkbpg-7RtzC2rq0pI")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@phantommetrics")

def send_deal_to_telegram(title: str, url: str, price: Optional[str] = None, description: Optional[str] = None) -> bool:
    """
    Send a deal notification to Telegram channel.
    
    Args:
        title: Deal title/name
        url: Deal URL link  
        price: Optional price (e.g., "£42.99", "$25.00")
        description: Optional deal description
        
    Returns:
        True if notification was sent successfully, False otherwise
    """
    
    # Format the message with HTML
    message = f"🔥 <b>New Deal Spotted!</b>\n📦 <b>Item:</b> {title}"
    
    if price:
        message += f"\n💸 <b>Price:</b> {price}"
    
    if description:
        # Truncate description if too long
        desc = description[:200] + "..." if len(description) > 200 else description
        message += f"\n📝 <b>Description:</b> {desc}"
    
    message += f"\n🔗 <a href='{url}'>View Deal</a>"
    
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHANNEL_ID,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            },
            timeout=10
        )
        
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ Deal notification sent: {title}")
            return True
        else:
            print(f"❌ Failed to send notification: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False

def send_simple_deal(title: str, url: str, price: Optional[str] = None) -> bool:
    """
    Simplified function to send a basic deal notification.
    
    Args:
        title: Deal title
        url: Deal URL
        price: Optional price
        
    Returns:
        True if successful, False otherwise
    """
    return send_deal_to_telegram(title, url, price)

# Example usage and test function
def test_notification():
    """Test the notification function with sample data."""
    print("Testing deal notification...")
    
    success = send_deal_to_telegram(
        title="LEGO Star Wars AT-AT Walker 75288",
        url="https://example.com/lego-deal",
        price="£42.99",
        description="Amazing deal on LEGO Star Wars set with free shipping!"
    )
    
    if success:
        print("✅ Test notification successful!")
    else:
        print("❌ Test notification failed!")
    
    return success

if __name__ == "__main__":
    # Run test when script is executed directly
    test_notification()