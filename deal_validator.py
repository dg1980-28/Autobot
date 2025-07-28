import re
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of deal validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class DealValidator:
    """
    Validator for deal data before sending notifications.
    Ensures data quality and prevents sending invalid or spam content.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # URL validation patterns
        self.valid_url_schemes = {'http', 'https'}
        
        # Price validation patterns
        self.price_patterns = [
            r'[\$£€¥₹][\d,]+\.?\d*',  # Currency symbols with numbers
            r'\d+[\.,]\d+\s*[\$£€¥₹]',  # Numbers with currency at end
            r'[\$£€¥₹]?\s*\d+[\.,]?\d*',  # General price pattern
            r'free|FREE',  # Free items
        ]
        
        # Spam/invalid content patterns
        self.spam_patterns = [
            r'[A-Z]{5,}',  # Too many consecutive capitals
            r'!{3,}',  # Too many exclamation marks
            r'www\..*\..*\..*',  # Suspicious nested domains
        ]
        
        # Title validation
        self.min_title_length = 3
        self.max_title_length = 200
        
        # Description validation
        self.max_description_length = 500
    
    def validate_url(self, url: str) -> ValidationResult:
        """Validate deal URL."""
        errors = []
        warnings = []
        
        if not url or not isinstance(url, str):
            errors.append("URL is required and must be a string")
            return ValidationResult(False, errors, warnings)
        
        url = url.strip()
        if not url:
            errors.append("URL cannot be empty")
            return ValidationResult(False, errors, warnings)
        
        try:
            parsed = urlparse(url)
            
            if not parsed.scheme:
                errors.append("URL must include a scheme (http/https)")
            elif parsed.scheme.lower() not in self.valid_url_schemes:
                errors.append(f"URL scheme must be one of: {', '.join(self.valid_url_schemes)}")
            
            if not parsed.netloc:
                errors.append("URL must include a domain")
            
            # Check for suspicious patterns
            if len(parsed.netloc.split('.')) > 4:
                warnings.append("Domain has many subdomains - may be suspicious")
                
        except Exception as e:
            errors.append(f"Invalid URL format: {str(e)}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def validate_title(self, title: str) -> ValidationResult:
        """Validate deal title."""
        errors = []
        warnings = []
        
        if not title or not isinstance(title, str):
            errors.append("Title is required and must be a string")
            return ValidationResult(False, errors, warnings)
        
        title = title.strip()
        if not title:
            errors.append("Title cannot be empty")
            return ValidationResult(False, errors, warnings)
        
        if len(title) < self.min_title_length:
            errors.append(f"Title must be at least {self.min_title_length} characters long")
        
        if len(title) > self.max_title_length:
            errors.append(f"Title must be no more than {self.max_title_length} characters long")
        
        # Check for spam patterns
        for pattern in self.spam_patterns:
            if re.search(pattern, title):
                warnings.append(f"Title may contain spam-like content: {pattern}")
        
        # Check for reasonable content
        if title.count(' ') == 0 and len(title) > 20:
            warnings.append("Title is very long without spaces - may be suspicious")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def validate_price(self, price: Optional[str]) -> ValidationResult:
        """Validate deal price."""
        errors = []
        warnings = []
        
        if price is None:
            return ValidationResult(True, errors, warnings)  # Price is optional
        
        if not isinstance(price, str):
            errors.append("Price must be a string")
            return ValidationResult(False, errors, warnings)
        
        price = price.strip()
        if not price:
            return ValidationResult(True, errors, warnings)  # Empty price is okay
        
        # Check if price matches expected patterns
        price_valid = False
        for pattern in self.price_patterns:
            if re.search(pattern, price, re.IGNORECASE):
                price_valid = True
                break
        
        if not price_valid:
            warnings.append("Price format doesn't match common patterns")
        
        # Check for suspicious price content
        if len(price) > 50:
            warnings.append("Price string is unusually long")
        
        return ValidationResult(True, errors, warnings)
    
    def validate_description(self, description: Optional[str]) -> ValidationResult:
        """Validate deal description."""
        errors = []
        warnings = []
        
        if description is None:
            return ValidationResult(True, errors, warnings)  # Description is optional
        
        if not isinstance(description, str):
            errors.append("Description must be a string")
            return ValidationResult(False, errors, warnings)
        
        description = description.strip()
        if not description:
            return ValidationResult(True, errors, warnings)  # Empty description is okay
        
        if len(description) > self.max_description_length:
            warnings.append(f"Description is longer than {self.max_description_length} characters and will be truncated")
        
        # Check for spam patterns
        for pattern in self.spam_patterns:
            if re.search(pattern, description):
                warnings.append(f"Description may contain spam-like content: {pattern}")
        
        return ValidationResult(True, errors, warnings)
    
    def validate_deal(self, title: str, url: str, price: Optional[str] = None, 
                     description: Optional[str] = None) -> ValidationResult:
        """
        Validate complete deal data.
        
        Args:
            title: Deal title
            url: Deal URL
            price: Optional price
            description: Optional description
            
        Returns:
            ValidationResult with overall validation status
        """
        all_errors = []
        all_warnings = []
        
        # Validate each component
        validations = [
            ("title", self.validate_title(title)),
            ("url", self.validate_url(url)),
            ("price", self.validate_price(price)),
            ("description", self.validate_description(description))
        ]
        
        for field_name, result in validations:
            if result.errors:
                all_errors.extend([f"{field_name}: {error}" for error in result.errors])
            if result.warnings:
                all_warnings.extend([f"{field_name}: {warning}" for warning in result.warnings])
        
        # Additional cross-field validations
        if title and url:
            # Check if URL domain matches title expectations
            try:
                domain = urlparse(url).netloc.lower()
                title_lower = title.lower()
                
                # List of known deal sites
                known_deal_sites = ['amazon', 'ebay', 'argos', 'currys', 'johnlewis', 'ao', 'very']
                
                # Check if title mentions a brand but URL is from a different site
                for site in known_deal_sites:
                    if site in title_lower and site not in domain:
                        all_warnings.append(f"Title mentions {site} but URL is from {domain}")
                        break
                        
            except Exception:
                pass  # Skip cross-validation if URL parsing fails
        
        is_valid = len(all_errors) == 0
        
        if all_warnings:
            self.logger.warning(f"Deal validation warnings: {'; '.join(all_warnings)}")
        
        if all_errors:
            self.logger.error(f"Deal validation errors: {'; '.join(all_errors)}")
        
        return ValidationResult(is_valid, all_errors, all_warnings)
