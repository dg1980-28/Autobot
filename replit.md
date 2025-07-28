# Deal Notification System

## Overview

This is a comprehensive Python-based deal scraping and notification system that monitors deal websites and sends formatted alerts to Telegram channels. The system uses web scraping techniques to extract deal information and provides a robust notification framework with validation, rate limiting, and error handling.

**Current Status**: Fully operational and tested successfully. Both Python direct integration and Flask HTTP API server confirmed working with @phantommetrics channel using Phantomdeals_bot. All notification methods tested and delivering successfully.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Configuration Management**: Centralized configuration handling with support for environment variables and config files
- **Web Scraping**: Content extraction using trafilatura and BeautifulSoup for parsing deal websites
- **Validation**: Deal data validation to ensure quality and prevent spam
- **Notification System**: Telegram bot integration with formatting and rate limiting
- **Main Orchestrator**: Coordinates all components and provides CLI interface

## Key Components

### Configuration Manager (`config_manager.py`)
- **Purpose**: Manages all system configuration including Telegram, scraping, and logging settings
- **Features**: Environment variable support, dataclass-based configuration, fallback to config files
- **Key Classes**: `TelegramConfig`, `ScrapingConfig`, `LoggingConfig`, `ConfigManager`

### Telegram Notifier (`telegram_notifier.py`)
- **Purpose**: Handles all Telegram communication with robust error handling
- **Features**: Rate limiting, retry logic, HTML/Markdown formatting, message templating
- **Key Classes**: `TelegramNotifier`, `MessageFormat` enum
- **API Integration**: Uses Telegram Bot API for sending messages to channels

### Deal Validator (`deal_validator.py`)
- **Purpose**: Validates deal data before sending notifications
- **Features**: URL validation, price pattern matching, spam detection, content length checks
- **Key Classes**: `DealValidator`, `ValidationResult`
- **Validation Rules**: URL scheme checking, price format validation, spam pattern detection

### Web Scraper Integration (`web_scraper_integration.py`)
- **Purpose**: Main scraping orchestrator that coordinates content extraction and notifications
- **Features**: Concurrent scraping, duplicate prevention, session management
- **Key Classes**: `DealScraper`
- **Dependencies**: Integrates trafilatura for content extraction

### Example Scrapers (`example_scraper.py`)
- **Purpose**: Demonstrates custom scraper implementations for specific websites
- **Features**: Site-specific parsing logic, BeautifulSoup integration
- **Example**: HotUKDeals scraper implementation

### Simple Integration (`send_deal_notification.py`)
- **Purpose**: Provides easy integration for existing web scrapers
- **Features**: Single function call to send deal notifications, automatic HTML formatting
- **Key Function**: `send_deal_to_telegram()` for direct integration with existing scrapers
- **Status**: Active and tested with successful Telegram delivery

### Flask HTTP Server (`phantom_bot_server.py`)
- **Purpose**: HTTP API server for universal language integration
- **Features**: REST API endpoints, health checks, JSON request/response, comprehensive logging
- **Key Endpoints**: POST `/send`, GET `/health`, GET `/`
- **Status**: Active and running on port 5000 with successful API testing
- **Integration**: Works with any programming language via HTTP requests

## Data Flow

1. **Configuration Loading**: System loads configuration from environment variables or config files
2. **Scraper Initialization**: Web scraper is initialized with configuration and creates Telegram notifier
3. **Content Extraction**: Trafilatura extracts main content from target URLs
4. **Deal Parsing**: Custom scrapers parse extracted content to identify deals
5. **Validation**: Deal validator checks data quality and filters spam
6. **Duplicate Check**: System prevents sending duplicate deals
7. **Notification**: Formatted messages are sent to Telegram with rate limiting
8. **Logging**: All operations are logged for monitoring and debugging

## External Dependencies

### Core Libraries
- **trafilatura**: Web content extraction and text processing
- **BeautifulSoup4**: HTML parsing for custom scrapers
- **requests**: HTTP client for API calls and web scraping

### Telegram Integration
- **Telegram Bot API**: Direct HTTP API integration for sending messages
- **Bot Token**: Required for authentication
- **Channel ID**: Target channel for notifications

### Configuration Sources
- **Environment Variables**: Primary configuration source
- **Config Files**: Fallback configuration option (JSON format implied)

## Deployment Strategy

### Environment Setup
- Python 3.x runtime required
- Environment variables for sensitive configuration (bot tokens, channel IDs)
- Logging to both console and file for monitoring

### Execution Modes
- **One-time Scraping**: Single execution for testing or manual runs
- **Continuous Monitoring**: Scheduled execution with configurable intervals
- **CLI Interface**: Command-line arguments for different operation modes

### Configuration Management
- Supports both development and production configurations
- Environment variable override system
- Secure handling of API tokens and credentials

### Error Handling
- Comprehensive logging at all levels
- Retry mechanisms for network operations
- Rate limiting to respect API constraints
- Graceful failure handling with detailed error messages

### Scalability Considerations
- Concurrent scraping support with configurable limits
- Session pooling for efficient HTTP connections
- Duplicate prevention to avoid spam
- Configurable timeouts and intervals