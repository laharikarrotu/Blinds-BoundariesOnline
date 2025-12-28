"""Repository for mask data access."""
import os
from pathlib import Path
from typing import Optional
from io import BytesIO
from app.core.config import config
from app.core.logger import logger
from app.core.exceptions import NotFoundError
from app.models.image import WindowMask
import numpy as np
from PIL import Image


class MaskRepository:
    """Repository for mask storage operations with Azure Blob Storage support."""
    
    def __init__(self, storage_repo=None):
        """
        Initialize mask repository.
        
        Args:
            storage_repo: Optional StorageRepository for Azure Blob Storage
        """
        self.mask_dir = Path(config.MASK_DIR)
        self.mask_dir.mkdir(exist_ok=True)
        self.storage_repo = storage_repo
    
    def save_mask(self, image_id: str, mask_array: np.ndarray) -> str:
        """
        Save mask array to Azure Blob Storage (primary) and local (fallback).
        
        Args:
            image_id: Image identifier
            mask_array: Mask as numpy array
            
        Returns:
            Path to saved mask (local path for compatibility)
        """
        mask_filename = f"mask_{image_id}.png"
        mask_path = self.mask_dir / mask_filename
        blob_name = f"masks/{mask_filename}"
        
        # Convert to PIL Image
        mask_image = Image.fromarray(mask_array.astype(np.uint8))
        
        # Try Azure Blob Storage first (scalable)
        if self.storage_repo and self.storage_repo.is_available():
            try:
                # Save to bytes buffer
                buffer = BytesIO()
                mask_image.save(buffer, format='PNG')
                buffer.seek(0)
                
                # Upload to Azure
                container_client = self.storage_repo.client.get_container_client(
                    self.storage_repo.container_name
                )
                
                if not container_client.exists():
                    container_client.create_container()
                
                blob_client = container_client.upload_blob(
                    name=blob_name,
                    data=buffer,
                    overwrite=True
                )
                
                logger.info(f"Mask {image_id} saved to Azure Blob Storage")
            except Exception as e:
                logger.warning(f"Azure mask upload failed, using local storage: {e}")
        
        # Always save locally for processing (masks are needed for image processing)
        mask_image.save(mask_path)
        
        return str(mask_path)
    
    def get_mask_path(self, image_id: str) -> Optional[Path]:
        """
        Get mask file path by image_id.
        Downloads from Azure if not found locally.
        
        Args:
            image_id: Image identifier
            
        Returns:
            Path to mask file or None if not found
        """
        mask_filename = f"mask_{image_id}.png"
        mask_path = self.mask_dir / mask_filename
        
        # Check local first
        if mask_path.exists():
            return mask_path
        
        # Try downloading from Azure
        if self.storage_repo and self.storage_repo.is_available():
            try:
                blob_name = f"masks/{mask_filename}"
                if self.storage_repo.download_file(blob_name, str(mask_path)):
                    logger.info(f"Downloaded mask {image_id} from Azure")
                    return mask_path
            except Exception as e:
                logger.warning(f"Failed to download mask from Azure: {e}")
        
        return None
    
    def get_mask(self, image_id: str) -> WindowMask:
        """
        Get mask data by image_id.
        
        Args:
            image_id: Image identifier
            
        Returns:
            WindowMask object
            
        Raises:
            NotFoundError: If mask not found
        """
        mask_path = self.get_mask_path(image_id)
        if not mask_path or not mask_path.exists():
            raise NotFoundError(f"Mask for image {image_id} not found")
        
        # Load mask to get dimensions
        with Image.open(mask_path) as mask_img:
            mask_array = np.array(mask_img)
            total_pixels = mask_array.size
            white_pixels = np.sum(mask_array > 128)
            coverage = (white_pixels / total_pixels) * 100 if total_pixels > 0 else 0
        
        return WindowMask(
            mask_path=str(mask_path),
            width=mask_img.width,
            height=mask_img.height,
            coverage_percentage=coverage
        )
    
    def delete_mask(self, image_id: str) -> bool:
        """
        Delete mask file.
        
        Args:
            image_id: Image identifier
            
        Returns:
            True if deleted, False if not found
        """
        mask_path = self.get_mask_path(image_id)
        if mask_path and mask_path.exists():
            mask_path.unlink()
            return True
        return False

