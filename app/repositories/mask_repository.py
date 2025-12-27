"""Repository for mask data access."""
import os
from pathlib import Path
from typing import Optional
from app.core.config import config
from app.core.exceptions import NotFoundError
from app.models.image import WindowMask
import numpy as np
from PIL import Image


class MaskRepository:
    """Repository for mask storage operations."""
    
    def __init__(self):
        self.mask_dir = Path(config.MASK_DIR)
        self.mask_dir.mkdir(exist_ok=True)
    
    def save_mask(self, image_id: str, mask_array: np.ndarray) -> str:
        """
        Save mask array to file.
        
        Args:
            image_id: Image identifier
            mask_array: Mask as numpy array
            
        Returns:
            Path to saved mask
        """
        mask_filename = f"mask_{image_id}.png"
        mask_path = self.mask_dir / mask_filename
        
        # Convert to PIL Image and save
        mask_image = Image.fromarray(mask_array.astype(np.uint8))
        mask_image.save(mask_path)
        
        return str(mask_path)
    
    def get_mask_path(self, image_id: str) -> Optional[Path]:
        """
        Get mask file path by image_id.
        
        Args:
            image_id: Image identifier
            
        Returns:
            Path to mask file or None if not found
        """
        mask_filename = f"mask_{image_id}.png"
        mask_path = self.mask_dir / mask_filename
        
        if mask_path.exists():
            return mask_path
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

