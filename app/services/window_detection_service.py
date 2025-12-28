"""Service for window detection operations."""
from typing import Optional
import numpy as np
from app.core.config import config
from app.core.logger import logger
from app.core.exceptions import WindowDetectionError
from app.repositories.mask_repository import MaskRepository
from app.repositories.storage_repository import StorageRepository
from app.cache.lru_cache import cache


class WindowDetectionService:
    """Service for window detection with caching."""
    
    def __init__(self, storage_repo=None):
        """
        Initialize window detection service.
        
        Args:
            storage_repo: Optional StorageRepository for Azure integration
        """
        self.storage_repo = storage_repo or StorageRepository()
        self.mask_repo = MaskRepository(storage_repo=self.storage_repo)
        self.detector = None
        self._initialize_detector()
    
    def _initialize_detector(self):
        """Initialize window detector."""
        try:
            # Try importing from app directory first
            try:
                from app.hybrid_detector import HybridWindowDetector
            except ImportError:
                # Fallback to root level import
                from hybrid_detector import HybridWindowDetector
            
            self.detector = HybridWindowDetector(
                gemini_api_key=config.GEMINI_API_KEY,
                azure_vision_key=config.AZURE_VISION_KEY,
                azure_vision_endpoint=config.AZURE_VISION_ENDPOINT
            )
            logger.info("Hybrid window detector initialized")
        except (ImportError, Exception) as e:
            logger.warning(f"Hybrid detector not available, using fallback: {e}")
            self.detector = None
    
    def detect_window(self, image_id: str, image_path: str) -> str:
        """
        Detect window in image and save mask.
        Uses caching to avoid redundant processing.
        
        Args:
            image_id: Image identifier
            image_path: Path to image file
            
        Returns:
            Path to saved mask
            
        Raises:
            WindowDetectionError: If detection fails
        """
        # Check cache first
        cache_key = f"mask:{image_id}"
        if config.ENABLE_CACHING:
            cached_mask_path = cache.get(cache_key)
            if cached_mask_path:
                logger.info(f"Using cached mask for {image_id}")
                return cached_mask_path
        
        try:
            # Generate mask path
            mask_path = self.mask_repo.get_mask_path(image_id)
            if not mask_path:
                mask_path = self.mask_repo.mask_dir / f"mask_{image_id}.png"
            
            # Run detection
            if self.detector:
                result = self.detector.detect_window(str(image_path), str(mask_path))
                if not result:
                    raise WindowDetectionError("Window detection returned no result")
            else:
                # Fallback: create simple mask
                self._create_fallback_mask(image_path, str(mask_path))
            
            # Upload to Azure if available
            azure_url = None
            if self.storage_repo.is_available():
                blob_name = f"masks/{Path(mask_path).name}"
                azure_url = self.storage_repo.upload_file(str(mask_path), blob_name)
            
            # Cache the result
            if config.ENABLE_CACHING:
                cache.set(cache_key, str(mask_path), ttl=config.CACHE_TTL)
            
            logger.info(f"Window detection completed for {image_id}")
            return str(mask_path)
            
        except Exception as e:
            error_msg = str(e)
            logger.exception(f"Window detection failed for {image_id}: {error_msg}")
            
            # Check if it's the libGL.so.1 error
            if 'libGL' in error_msg or 'libGL.so' in error_msg:
                raise WindowDetectionError(
                    "Window detection failed: OpenCV requires libGL.so.1 which is not available on Azure App Service. "
                    "Please ensure Azure Computer Vision or Gemini API is configured for window detection."
                )
            
            raise WindowDetectionError(f"Window detection failed: {error_msg}")
    
    def _create_fallback_mask(self, image_path: str, mask_path: str):
        """Create simple fallback mask."""
        import cv2
        image = cv2.imread(image_path)
        if image is None:
            raise WindowDetectionError("Could not read image")
        
        height, width = image.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # Create center rectangle
        x1, y1 = width // 4, height // 4
        x2, y2 = 3 * width // 4, 3 * height // 4
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
        
        cv2.imwrite(mask_path, mask)

