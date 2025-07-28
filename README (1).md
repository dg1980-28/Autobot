# Deal Notification System

A Python system that automatically sends deal alerts to your Telegram channel whenever new deals are found by your web scraper.

## 🚀 Two Ways to Use This System

### Option 1: Direct Python Integration (Simple)

Perfect if you have a Python scraper and want to call a function directly.

```python
from send_deal_notification import send_deal_to_telegram

# When your scraper finds a deal, call this function:
send_deal_to_telegram(
    title="LEGO Star Wars AT-AT Walker",
    url="https://example.com/deal-link", 
    price="£42.99",  # Optional
    description="Great deal with free shipping!"  # Optional
)
```

### Option 2: HTTP API Server (Universal)

Perfect for any programming language or external systems. Start the Flask server and send HTTP requests.

**Start the server:**
```bash
python phantom_bot_server.py
```

**Send deals via HTTP:**
```bash
curl -X POST http://localhost:5000/send \
  -H "Content-Type: application/json" \
  -d '{
    "title": "LEGO Millennium Falcon",
    "url": "https://deals.com/lego",
    "price": "£89.99",
    "description": "Limited time offer!"
  }'
```

## 🧪 Test Your Setup

**Option 1 - Test Python integration:**
```bash
python send_deal_notification.py
```

**Option 2 - Test Flask server:**
```bash
# Terminal 1: Start server
python phantom_bot_server.py

# Terminal 2: Send test request
curl -X GET http://localhost:5000/health
```

You should see success messages and receive notifications in your Telegram channel.

### 3. Integration Examples

**Basic Integration:**
```python
# In your existing scraper code:
from send_deal_notification import send_simple_deal

def process_found_deal(deal_info):
    # Your existing deal processing logic
    title = deal_info['name']
    url = deal_info['link'] 
    price = deal_info.get('price')
    
    # Send to Telegram
    send_simple_deal(title, url, price)
```

**Advanced Integration:**
```python
from send_deal_notification import send_deal_to_telegram

def notify_new_deal(title, url, price=None, description=None):
    success = send_deal_to_telegram(title, url, price, description)
    if success:
        print(f"Notified about: {title}")
    else:
        print(f"Failed to notify about: {title}")
    return success
```

## Configuration

### Environment Variables (Recommended)

Create a `.env` file with your configuration:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_here
```

### Fallback Configuration

The system includes fallback configuration for quick testing, but for production use, always set environment variables to keep your bot token secure.

## Advanced Features

### Full System with Web Scraping

If you want to use the complete scraping and notification system:

```bash
# Test the full system
python main.py test

# Scrape a single website
python main.py scrape --url "https://example-deals-site.com"

# Monitor multiple sites continuously  
python main.py monitor --urls "https://site1.com" "https://site2.com"

# Send a custom notification
python main.py notify --title "Custom Deal" --url "https://example.com" --price "£25.00"
```

### Custom Deal Validation

The system includes automatic validation to ensure quality notifications:
- URL format checking
- Price pattern validation
- Spam detection
- Duplicate prevention

### Rate Limiting & Error Handling

- Automatic retry on failures
- Rate limiting to respect Telegram limits
- Comprehensive error logging
- Connection testing

📖 For detailed Flask server documentation, see [SERVER_API.md](SERVER_API.md)

## Files Overview

**Main Integration Files:**
- `send_deal_notification.py` - Direct Python integration (simple)
- `phantom_bot_server.py` - Flask HTTP API server (universal)

**Advanced System Files:**
- `main.py` - Full system with CLI interface
- `telegram_notifier.py` - Advanced notification features
- `deal_validator.py` - Deal validation logic
- `web_scraper_integration.py` - Web scraping integration
- `example_scraper.py` - Examples for specific websites

**Documentation:**
- `README.md` - This file (quick start guide)
- `SERVER_API.md` - Detailed Flask server API documentation

## Troubleshooting

**"Failed to send notification" errors:**
- Check your internet connection
- Verify the bot token is correct
- Make sure the bot is added to your channel as an admin

**"Bot connection failed":**
- The bot token may be invalid
- Check if the bot was deleted or blocked

**No messages received:**
- Verify the channel ID is correct (@phantommetrics)
- Make sure the channel is public or the bot is an admin
- Check if the channel exists and is accessible

## Installation

Clone the repository and install dependencies:

```bash
git clone <your-repo-url>
cd deal-notification-system
pip install requests beautifulsoup4 trafilatura
```

## Support

The system includes detailed logging. Check the console output and `deal_notifier.log` file for error details.

## Security Note

Never commit your bot token to GitHub. Always use environment variables or a `.env` file (which is ignored by git) for sensitive configuration.