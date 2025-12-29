"""Configuration management using environment variables."""
import os
from typing import Optional
from functools import lru_cache

# Try to load .env file, but don't fail if it doesn't exist or can't be read
try:
    from dotenv import load_dotenv
    load_dotenv()
except (ImportError, PermissionError, FileNotFoundError):
    # .env file not available or can't be read - use environment variables only
    pass


@lru_cache()
class Config:
    """Singleton configuration class with cached values."""
    
    # Azure Configuration
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER: str = os.getenv("AZURE_STORAGE_CONTAINER", "window-images")
    AZURE_VISION_KEY: Optional[str] = os.getenv("AZURE_VISION_KEY")
    AZURE_VISION_ENDPOINT: Optional[str] = os.getenv("AZURE_VISION_ENDPOINT")
    
    # API Keys
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Frontend Configuration
    FRONTEND_URL: Optional[str] = os.getenv("FRONTEND_URL")
    
    # Directories
    UPLOAD_DIR: str = "uploads"
    MASK_DIR: str = "masks"
    BLINDS_DIR: str = "blinds"
    RESULTS_DIR: str = "results"
    
    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", 3600))  # 1 hour
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", 1000))
    
    # Processing Configuration
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", 10))
    
    # Performance
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    ENABLE_ASYNC: bool = os.getenv("ENABLE_ASYNC", "true").lower() == "true"
    
    @property
    def azure_available(self) -> bool:
        """Check if Azure is configured."""
        return self.AZURE_STORAGE_CONNECTION_STRING is not None
    
    @property
    def azure_vision_available(self) -> bool:
        """Check if Azure Vision is configured."""
        return self.AZURE_VISION_KEY is not None and self.AZURE_VISION_ENDPOINT is not None
    
    @property
    def gemini_available(self) -> bool:
        """Check if Gemini API is configured."""
        return self.GEMINI_API_KEY is not None


config = Config()

