# Phantom Bot Server API

A Flask web server that receives deal notifications via HTTP requests and sends them to your Telegram channel.

## 🚀 Quick Start

1. **Start the server:**
   ```bash
   python phantom_bot_server.py
   ```
   Server runs on `http://localhost:5000`

2. **Send a deal notification:**
   ```bash
   curl -X POST http://localhost:5000/send \
     -H "Content-Type: application/json" \
     -d '{
       "title": "LEGO Star Wars AT-AT",
       "url": "https://example.com/deal",
       "price": "£42.99",
       "description": "Amazing deal with free shipping!"
     }'
   ```

## 📡 API Endpoints

### POST /send
Send a deal notification to Telegram.

**Request Body:**
```json
{
  "title": "Deal title (required)",
  "url": "Deal URL (required)",
  "price": "Price (optional)",
  "description": "Deal description (optional)"
}
```

**Response:**
```json
{
  "ok": true,
  "processed": true,
  "timestamp": "2025-07-28T15:23:17.754124",
  "result": { /* Telegram API response */ }
}
```

### GET /health
Check server and bot status.

**Response:**
```json
{
  "status": "healthy",
  "bot_username": "Phantomdeals_bot",
  "channel": "@phantommetrics",
  "timestamp": "2025-07-28T15:23:12.544150"
}
```

### GET /
Server information and usage guide.

## 🔌 Integration Examples

### Python Requests
```python
import requests

def send_deal_via_api(title, url, price=None, description=None):
    data = {
        "title": title,
        "url": url,
        "price": price,
        "description": description
    }
    
    response = requests.post(
        "http://localhost:5000/send",
        json=data
    )
    
    return response.json()

# Usage
result = send_deal_via_api(
    title="LEGO Millennium Falcon",
    url="https://deals.com/lego",
    price="£89.99"
)
```

### JavaScript/Node.js
```javascript
async function sendDeal(title, url, price, description) {
    const response = await fetch('http://localhost:5000/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            title,
            url,
            price,
            description
        })
    });
    
    return await response.json();
}
```

### PHP
```php
function sendDeal($title, $url, $price = null, $description = null) {
    $data = [
        'title' => $title,
        'url' => $url,
        'price' => $price,
        'description' => $description
    ];
    
    $ch = curl_init('http://localhost:5000/send');
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    
    $result = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($result, true);
}
```

## 🛠️ Configuration

The server uses environment variables or fallback values:

```bash
# Environment variables (recommended)
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHANNEL_ID="@your_channel_here"

# Start server
python phantom_bot_server.py
```

## 🔍 Monitoring

- **Logs:** Check console output for request logs and errors
- **Health Check:** GET `/health` to verify bot connection
- **Error Handling:** All endpoints return proper HTTP status codes

## ⚡ Performance

- **Response Time:** Typically under 1 second
- **Rate Limiting:** Handles Telegram API rate limits automatically
- **Error Recovery:** Automatic retry logic and detailed error reporting

## 🔒 Security Notes

- Server runs on localhost by default
- Use environment variables for production secrets
- Consider adding authentication for production deployments