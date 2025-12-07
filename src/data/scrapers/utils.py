"""
Utility functions for web scraping
Rate limiting, retries, session management
"""

import time
import requests
from typing import Optional, Callable, Any
from functools import wraps
import random

from src.utils import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Simple rate limiter with configurable delay
    """
    
    def __init__(self, min_delay: float = 2.0, max_delay: float = 4.0):
        """
        Initialize rate limiter
        
        Args:
            min_delay: Minimum seconds between requests
            max_delay: Maximum seconds (adds randomness)
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
    
    def wait(self):
        """
        Wait if necessary to respect rate limit
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Random delay between min and max (looks more human)
        delay = random.uniform(self.min_delay, self.max_delay)
        
        if time_since_last < delay:
            sleep_time = delay - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()


def retry_on_failure(max_retries: int = 3, backoff_factor: float = 2.0):
    """
    Decorator to retry function on failure with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for delay between retries
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except requests.exceptions.RequestException as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        delay = backoff_factor ** attempt
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator


class SessionManager:
    """
    Manage HTTP sessions with connection pooling and headers
    """
    
    def __init__(
        self,
        user_agent: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3
    ):
        """
        Initialize session manager
        
        Args:
            user_agent: Custom User-Agent string
            timeout: Request timeout in seconds
            max_retries: Max retries per request
        """
        self.session = requests.Session()
        self.timeout = timeout
        
        # Set headers
        if user_agent is None:
            user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Configure retries
        adapter = requests.adapters.HTTPAdapter(
            max_retries=max_retries,
            pool_connections=10,
            pool_maxsize=20
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        logger.info("Session manager initialized")
    
    @retry_on_failure(max_retries=3)
    def get(self, url: str, **kwargs) -> requests.Response:
        """
        GET request with retries
        
        Args:
            url: URL to fetch
            **kwargs: Additional requests.get() parameters
            
        Returns:
            Response object
            
        Raises:
            RequestException if all retries fail
        """
        kwargs.setdefault('timeout', self.timeout)
        
        logger.debug(f"GET {url}")
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        
        return response
    
    def close(self):
        """Close the session"""
        self.session.close()
        logger.info("Session closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def validate_url(url: str) -> bool:
    """
    Basic URL validation
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not url:
        return False
    
    if not url.startswith(('http://', 'https://')):
        return False
    
    return True


def sanitize_text(text: str) -> str:
    """
    Clean and normalize text from web scraping
    
    Args:
        text: Raw text string
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters (keep basic punctuation)
    text = text.strip()
    
    return text