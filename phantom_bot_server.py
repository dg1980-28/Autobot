from flask import Flask, request, jsonify
import requests
import os
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot credentials - use environment variables or fallback
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8221917763:AAGGzoTtDPmgdo4etyNkbpg-7RtzC2rq0pI")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@phantommetrics")

def send_telegram_message(title, url, price=None, description=None):
    """Send formatted deal message to Telegram channel."""
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
            logger.info(f"Deal notification sent successfully: {title}")
        else:
            logger.error(f"Telegram API error: {result.get('description', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return {"ok": False, "error": str(e)}

@app.route('/send', methods=['POST'])
def handle_deal():
    """Handle incoming deal notification requests."""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        title = data.get("title")
        url = data.get("url")
        price = data.get("price")
        description = data.get("description")

        # Validate required fields
        if not title or not url:
            return jsonify({"error": "Missing required fields: title and url"}), 400

        # Log the incoming request
        logger.info(f"Received deal notification request: {title}")
        
        # Send to Telegram
        result = send_telegram_message(title, url, price, description)
        
        # Add timestamp to response
        result["timestamp"] = datetime.now().isoformat()
        result["processed"] = True
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing deal request: {e}")
        return jsonify({"error": str(e), "ok": False}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test Telegram bot connection
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=5)
        bot_info = response.json()
        
        if bot_info.get("ok"):
            return jsonify({
                "status": "healthy",
                "bot_username": bot_info.get("result", {}).get("username"),
                "channel": CHANNEL_ID,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "unhealthy", 
                "error": "Bot connection failed"
            }), 503
            
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503

@app.route("/", methods=["GET"])
def home():
    """Home page with status information."""
    return jsonify({
        "service": "Phantom Telegram Bot Server",
        "status": "live",
        "endpoints": {
            "POST /send": "Send deal notification",
            "GET /health": "Health check",
            "GET /": "This page"
        },
        "usage": {
            "send_deal": {
                "method": "POST",
                "url": "/send",
                "body": {
                    "title": "Deal title (required)",
                    "url": "Deal URL (required)", 
                    "price": "Price (optional)",
                    "description": "Description (optional)"
                }
            }
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting Phantom Bot Server...")
    logger.info(f"Telegram Channel: {CHANNEL_ID}")
    app.run(host="0.0.0.0", port=5000, debug=False)