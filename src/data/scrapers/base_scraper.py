"""
Abstract base class for all data scrapers
Provides common interface and validation logic
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime
from pathlib import Path
import hashlib

from src.utils import get_logger, ensure_dir


class BaseScraper(ABC):
    """
    Abstract base class for data acquisition from any source
    
    All scrapers must implement:
    - fetch_data()
    - parse_response()
    
    Common functionality provided:
    - Caching
    - Validation
    - Data normalization
    """
    
    def __init__(
        self,
        cache_dir: str = "data/raw",
        cache_enabled: bool = True,
        cache_ttl_days: int = 7
    ):
        """
        Initialize base scraper
        
        Args:
            cache_dir: Directory for caching raw data
            cache_enabled: Whether to use file cache
            cache_ttl_days: Cache time-to-live in days
        """
        self.logger = get_logger(self.__class__.__name__)
        self.cache_dir = ensure_dir(cache_dir)
        self.cache_enabled = cache_enabled
        self.cache_ttl_days = cache_ttl_days
        
        self.logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> Any:
        """
        Fetch raw data from source
        
        Must be implemented by subclasses
        Returns raw response (HTML, JSON, etc.)
        """
        pass
    
    @abstractmethod
    def parse_response(self, response: Any) -> pd.DataFrame:
        """
        Parse raw response into structured DataFrame
        
        Must be implemented by subclasses
        Returns DataFrame with standardized columns
        """
        pass
    
    def get_cached_data(self, cache_key: str) -> Optional[pd.DataFrame]:
        """
        Check if cached data exists and is fresh
        
        Args:
            cache_key: Unique identifier for cached file
            
        Returns:
            DataFrame if cache hit and fresh, None otherwise
        """
        if not self.cache_enabled:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.csv"
        
        if not cache_file.exists():
            self.logger.debug(f"Cache miss: {cache_key}")
            return None
        
        # Check if cache is stale
        file_age_days = (datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)).days
        
        if file_age_days > self.cache_ttl_days:
            self.logger.info(f"Cache stale ({file_age_days} days old): {cache_key}")
            return None
        
        self.logger.info(f"Cache hit ({file_age_days} days old): {cache_key}")
        return pd.read_csv(cache_file)
    
    def save_to_cache(self, data: pd.DataFrame, cache_key: str) -> None:
        """
        Save DataFrame to cache
        
        Args:
            data: DataFrame to cache
            cache_key: Unique identifier for cache file
        """
        if not self.cache_enabled:
            return
        
        cache_file = self.cache_dir / f"{cache_key}.csv"
        data.to_csv(cache_file, index=False)
        self.logger.info(f"Saved to cache: {cache_key} ({len(data)} rows)")
    
    def validate_data(self, df: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
        """
        Validate and clean DataFrame
        
        Args:
            df: Input DataFrame
            required_columns: List of required column names
            
        Returns:
            Cleaned DataFrame
            
        Raises:
            ValueError if required columns missing
        """
        # Check required columns
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['address'], keep='first')
        
        if len(df) < initial_count:
            self.logger.warning(f"Removed {initial_count - len(df)} duplicate addresses")
        
        # Remove rows with null required fields
        df = df.dropna(subset=required_columns)
        
        self.logger.info(f"Validated data: {len(df)} rows, {len(df.columns)} columns")
        
        return df
    
    def filter_geography(
        self,
        df: pd.DataFrame,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float
    ) -> pd.DataFrame:
        """
        Filter DataFrame to geographic bounds
        
        Args:
            df: Input DataFrame with 'lat' and 'lon' columns
            lat_min, lat_max, lon_min, lon_max: Bounding box
            
        Returns:
            Filtered DataFrame
        """
        if 'lat' not in df.columns or 'lon' not in df.columns:
            self.logger.warning("No lat/lon columns - skipping geographic filter")
            return df
        
        initial_count = len(df)
        
        df = df[
            (df['lat'] >= lat_min) &
            (df['lat'] <= lat_max) &
            (df['lon'] >= lon_min) &
            (df['lon'] <= lon_max)
        ]
        
        filtered_count = initial_count - len(df)
        if filtered_count > 0:
            self.logger.info(f"Filtered {filtered_count} properties outside geographic bounds")
        
        return df
    
    def generate_cache_key(self, **kwargs) -> str:
        """
        Generate unique cache key from parameters
        
        Args:
            **kwargs: Parameters to hash
            
        Returns:
            MD5 hash string
        """
        # Sort kwargs for consistent hashing
        key_string = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:12]
        
        # Include timestamp for readability
        timestamp = datetime.now().strftime("%Y%m")
        
        return f"{self.__class__.__name__.lower()}_{timestamp}_{key_hash}"
    
    def scrape(self, use_cache: bool = True, **kwargs) -> pd.DataFrame:
        """
        Main scraping workflow (template method pattern)
        
        Args:
            use_cache: Whether to check cache first
            **kwargs: Parameters passed to fetch_data()
            
        Returns:
            Cleaned DataFrame
        """
        # Generate cache key
        cache_key = self.generate_cache_key(**kwargs)
        
        # Check cache
        if use_cache:
            cached = self.get_cached_data(cache_key)
            if cached is not None:
                return cached
        
        # Fetch fresh data
        self.logger.info(f"Fetching fresh data with params: {kwargs}")
        raw_response = self.fetch_data(**kwargs)
        
        # Parse response
        df = self.parse_response(raw_response)
        
        # Save to cache
        self.save_to_cache(df, cache_key)
        
        return df