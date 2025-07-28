import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class TelegramConfig:
    """Configuration class for Telegram settings."""
    bot_token: str
    channel_id: str
    format_type: str = "HTML"  # HTML or Markdown
    max_retries: int = 3
    retry_delay: float = 2.0
    rate_limit_interval: float = 1.0
    disable_web_page_preview: bool = False

@dataclass
class ScrapingConfig:
    """Configuration class for scraping settings."""
    scrape_interval: int = 300  # 5 minutes
    max_concurrent_scrapes: int = 5
    request_timeout: int = 10
    user_agent: str = "Deal Scraper Bot 1.0"

@dataclass
class LoggingConfig:
    """Configuration class for logging settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = "deal_notifier.log"

class ConfigManager:
    """
    Configuration manager for the deal notification system.
    Supports environment variables, config files, and default values.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        
    def load_telegram_config(self) -> TelegramConfig:
        """Load Telegram configuration from environment variables or config file."""
        
        # Try to load from environment variables first
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        
        # If not found in env vars, try config file
        if not bot_token or not channel_id:
            if self.config_file and os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r') as f:
                        config_data = json.load(f)
                        telegram_config = config_data.get("telegram", {})
                        bot_token = bot_token or telegram_config.get("bot_token")
                        channel_id = channel_id or telegram_config.get("channel_id")
                except Exception as e:
                    self.logger.error(f"Failed to load config file: {e}")
        
        # Use hardcoded values as fallback (from uploaded files)
        if not bot_token:
            bot_token = "8221917763:AAGGzoTtDPmgdo4etyNkbpg-7RtzC2rq0pI"
            self.logger.warning("Using fallback bot token")
            
        if not channel_id:
            channel_id = "@phantommetrics"
            self.logger.warning("Using fallback channel ID")
        
        return TelegramConfig(
            bot_token=bot_token,
            channel_id=channel_id,
            format_type=os.getenv("TELEGRAM_FORMAT", "HTML"),
            max_retries=int(os.getenv("TELEGRAM_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("TELEGRAM_RETRY_DELAY", "2.0")),
            rate_limit_interval=float(os.getenv("TELEGRAM_RATE_LIMIT", "1.0")),
            disable_web_page_preview=os.getenv("TELEGRAM_DISABLE_PREVIEW", "false").lower() == "true"
        )
    
    def load_scraping_config(self) -> ScrapingConfig:
        """Load scraping configuration."""
        return ScrapingConfig(
            scrape_interval=int(os.getenv("SCRAPE_INTERVAL", "300")),
            max_concurrent_scrapes=int(os.getenv("MAX_CONCURRENT_SCRAPES", "5")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "10")),
            user_agent=os.getenv("USER_AGENT", "Deal Scraper Bot 1.0")
        )
    
    def load_logging_config(self) -> LoggingConfig:
        """Load logging configuration."""
        return LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_path=os.getenv("LOG_FILE", "deal_notifier.log")
        )
    
    def setup_logging(self) -> None:
        """Setup logging based on configuration."""
        config = self.load_logging_config()
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, config.level.upper()),
            format=config.format,
            handlers=[
                logging.StreamHandler(),  # Console output
                logging.FileHandler(config.file_path) if config.file_path else logging.NullHandler()
            ]
        )
    
    def save_config_template(self, file_path: str = "config.json") -> None:
        """Save a configuration template file."""
        template_config = {
            "telegram": asdict(TelegramConfig(
                bot_token="YOUR_BOT_TOKEN_HERE",
                channel_id="@your_channel_here"
            )),
            "scraping": asdict(ScrapingConfig()),
            "logging": asdict(LoggingConfig())
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(template_config, f, indent=2)
            self.logger.info(f"Configuration template saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save config template: {e}")
