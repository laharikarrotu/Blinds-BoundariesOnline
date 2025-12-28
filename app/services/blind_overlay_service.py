"""Service for blind overlay operations."""
import os
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Optional
from app.core.config import config
from app.core.logger import logger
from app.core.exceptions import BlindOverlayError
from app.models.blind import BlindData
from app.repositories.image_repository import ImageRepository
from app.repositories.mask_repository import MaskRepository
from app.repositories.storage_repository import StorageRepository
from app.algorithms.image_optimizer import ImageOptimizer
from app.cache.lru_cache import cache
from app.services.blind_factory import BlindGeneratorFactory


class BlindOverlayService:
    """Service for applying blind overlays with optimization."""
    
    def __init__(self, storage_repo=None):
        """
        Initialize blind overlay service.
        
        Args:
            storage_repo: Optional StorageRepository for Azure integration
        """
        self.storage_repo = storage_repo or StorageRepository()
        self.image_repo = ImageRepository(storage_repo=self.storage_repo)
        self.mask_repo = MaskRepository(storage_repo=self.storage_repo)
        self.optimizer = ImageOptimizer()
    
    def apply_blind_overlay(
        self,
        image_id: str,
        blind_data: BlindData,
        result_filename: Optional[str] = None
    ) -> str:
        """
        Apply blind overlay to image.
        Uses optimized algorithms and caching.
        
        Args:
            image_id: Image identifier
            blind_data: Blind configuration
            result_filename: Optional result filename
            
        Returns:
            Path to result image
            
        Raises:
            BlindOverlayError: If overlay fails
        """
        # Check cache
        cache_key = f"tryon:{image_id}:{hash(str(blind_data.to_dict()))}"
        if config.ENABLE_CACHING:
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Using cached result for {image_id}")
                return cached_result
        
        try:
            # Load image and mask
            image_data = self.image_repo.get_image_data(image_id)
            mask_data = self.mask_repo.get_mask(image_id)
            
            # Load images
            original_image = Image.open(image_data.file_path)
            mask_image = Image.open(mask_data.mask_path).convert('L')
            
            # Resize mask to match image (critical for dimension matching)
            if mask_image.size != original_image.size:
                logger.info(f"Resizing mask from {mask_image.size} to {original_image.size}")
                mask_image = mask_image.resize(original_image.size, Image.LANCZOS)
            
            # Generate blind overlay using factory pattern
            generator = BlindGeneratorFactory.create(blind_data)
            blind_overlay = generator.generate(
                original_image.width,
                original_image.height,
                blind_data
            )
            
            # Apply overlay using optimized algorithm
            result_image = self._apply_overlay_optimized(
                original_image, mask_image, blind_overlay
            )
            
            # Save result
            if not result_filename:
                result_filename = f"tryon_{image_id}_{blind_data.blind_name or blind_data.blind_type or 'custom'}.png"
            
            # Use /tmp for results on Azure App Service (read-only filesystem)
            if os.path.exists('/tmp') and os.access('/tmp', os.W_OK):
                result_path = Path('/tmp') / 'results' / result_filename
            else:
                result_path = Path(config.RESULTS_DIR) / result_filename
            
            try:
                result_path.parent.mkdir(parents=True, exist_ok=True)
                result_image.save(result_path)
            except (PermissionError, OSError) as e:
                # Read-only file system - use /tmp
                if not str(result_path).startswith('/tmp'):
                    result_path = Path('/tmp') / 'results' / result_filename
                    result_path.parent.mkdir(parents=True, exist_ok=True)
                    result_image.save(result_path)
                else:
                    raise
            
            # Upload to Azure if available
            azure_url = None
            if self.storage_repo.is_available():
                blob_name = f"results/{result_filename}"
                azure_url = self.storage_repo.upload_file(str(result_path), blob_name)
            
            # Cache result (use Azure URL if available, otherwise local path)
            result_url = azure_url if azure_url else str(result_path)
            if config.ENABLE_CACHING:
                cache.set(cache_key, result_url, ttl=config.CACHE_TTL)
            
            logger.info(f"Blind overlay completed for {image_id}")
            return result_url
            
        except Exception as e:
            error_msg = str(e) if str(e) else repr(e) or "Unknown error"
            logger.exception(f"Blind overlay failed for {image_id}: {error_msg}")
            raise BlindOverlayError(f"Blind overlay failed: {error_msg}")
    
    def _apply_overlay_optimized(
        self,
        original: Image.Image,
        mask: Image.Image,
        blind_overlay: Image.Image
    ) -> Image.Image:
        """
        Apply overlay using optimized algorithms.
        Uses vectorized operations for maximum performance.
        """
        # Convert to arrays
        original_array = np.array(original.convert('RGBA'))
        blind_array = np.array(blind_overlay.convert('RGBA'))
        mask_array = np.array(mask)
        
        # Use optimized blending (alpha based on mode)
        alpha = 0.9 if blind_overlay.mode == 'RGBA' else 0.8
        result_array = self.optimizer.apply_mask_efficient(
            original_array, mask_array, blind_array, alpha=alpha
        )
        
        return Image.fromarray(result_array)

