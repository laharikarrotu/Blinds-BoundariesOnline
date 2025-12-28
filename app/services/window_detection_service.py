"""Service for window detection operations."""
from typing import Optional
from pathlib import Path
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
        """Create smart fallback mask using PIL/NumPy edge detection (no OpenCV)."""
        from PIL import Image as PILImage, ImageFilter
        
        try:
            # Load image with PIL
            image = PILImage.open(image_path)
            width, height = image.size
            
            # Convert to grayscale for edge detection
            gray = image.convert('L')
            
            # Apply edge detection using PIL filters (no OpenCV needed)
            # Use FIND_EDGES filter to detect window boundaries
            edges = gray.filter(ImageFilter.FIND_EDGES)
            edges_array = np.array(edges)
            
            # Threshold edges to get strong edges (window frames)
            # Window frames are typically darker/brighter than surroundings
            edge_threshold = np.percentile(edges_array, 75)  # Top 25% of edge values
            strong_edges = (edges_array > edge_threshold).astype(np.uint8) * 255
            
            # Find rectangular regions (likely windows)
            # Look for horizontal and vertical lines (window frames)
            mask = np.zeros((height, width), dtype=np.uint8)
            
            # Strategy 1: Find largest rectangular region with strong edges
            # This typically corresponds to window frames
            # Use morphological operations (dilation) to connect edge fragments
            from scipy.ndimage import binary_dilation, binary_erosion
            
            # Dilate edges to connect window frame segments
            kernel = np.ones((5, 5), dtype=bool)
            dilated_edges = binary_dilation(strong_edges > 128, structure=kernel)
            
            # Find bounding box of largest connected region
            # This should be the window area
            rows = np.any(dilated_edges, axis=1)
            cols = np.any(dilated_edges, axis=0)
            
            if np.any(rows) and np.any(cols):
                # Found a region - use it as window mask
                y_min, y_max = np.where(rows)[0][[0, -1]]
                x_min, x_max = np.where(cols)[0][[0, -1]]
                
                # Add padding (10% of region size, min 20px)
                padding_x = max(20, int((x_max - x_min) * 0.1))
                padding_y = max(20, int((y_max - y_min) * 0.1))
                
                x_min = max(0, x_min - padding_x)
                y_min = max(0, y_min - padding_y)
                x_max = min(width, x_max + padding_x)
                y_max = min(height, y_max + padding_y)
                
                # Fill the window region
                mask[y_min:y_max, x_min:x_max] = 255
            else:
                # Fallback: Use center rectangle but make it smarter
                # Look for bright/dark regions (window glass vs frame)
                gray_array = np.array(gray)
                
                # Find center region with consistent brightness (likely window glass)
                center_x, center_y = width // 2, height // 2
                center_region_size = min(width, height) // 3
                
                x1 = max(0, center_x - center_region_size // 2)
                y1 = max(0, center_y - center_region_size // 2)
                x2 = min(width, center_x + center_region_size // 2)
                y2 = min(height, center_y + center_region_size // 2)
                
                mask[y1:y2, x1:x2] = 255
            
            # Apply soft edges to mask for better blending (avoid black spots)
            from scipy.ndimage import gaussian_filter
            blurred_mask = gaussian_filter(mask.astype(float), sigma=3)
            mask = (blurred_mask > 50).astype(np.uint8) * 255
            
            # Save mask using PIL
            mask_image = PILImage.fromarray(mask)
            mask_image.save(mask_path)
            logger.info(f"Smart fallback mask created: {mask_path}")
        except ImportError as e:
            # If scipy not available, use simple but improved fallback
            logger.warning(f"scipy not available for smart mask, using simple fallback: {e}")
            try:
                image = PILImage.open(image_path)
                width, height = image.size
                
                # Improved simple mask: larger center region with soft edges
                mask = np.zeros((height, width), dtype=np.uint8)
                # Use larger region (20% to 80% instead of 25% to 75%)
                x1, y1 = int(width * 0.2), int(height * 0.2)
                x2, y2 = int(width * 0.8), int(height * 0.8)
                
                # Create soft edges using gradient
                for y in range(y1, y2):
                    for x in range(x1, x2):
                        # Calculate distance from edges for soft blending
                        dist_x = min(x - x1, x2 - x) / ((x2 - x1) / 2)
                        dist_y = min(y - y1, y2 - y) / ((y2 - y1) / 2)
                        dist = min(dist_x, dist_y)
                        # Soft edge: 0.3 to 1.0
                        mask[y, x] = int(255 * max(0.3, dist))
                
                mask_image = PILImage.fromarray(mask)
                mask_image.save(mask_path)
            except Exception as e2:
                raise WindowDetectionError(f"Could not create fallback mask: {e2}")
        except Exception as e:
            raise WindowDetectionError(f"Could not create fallback mask: {e}")

