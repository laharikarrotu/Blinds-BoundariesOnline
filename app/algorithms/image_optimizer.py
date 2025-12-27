"""Optimized image processing algorithms."""
import numpy as np
from PIL import Image
from typing import Tuple, Optional
import cv2


class ImageOptimizer:
    """Efficient image processing algorithms."""
    
    @staticmethod
    def resize_with_aspect_ratio(
        image: np.ndarray,
        max_width: int,
        max_height: int,
        maintain_aspect: bool = True
    ) -> np.ndarray:
        """
        Resize image maintaining aspect ratio.
        O(n) where n is number of pixels.
        
        Args:
            image: Input image as numpy array
            max_width: Maximum width
            max_height: Maximum height
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        
        if not maintain_aspect:
            return cv2.resize(image, (max_width, max_height), interpolation=cv2.INTER_LANCZOS4)
        
        # Calculate scaling factor
        scale = min(max_width / width, max_height / height)
        
        if scale >= 1.0:
            return image  # No need to upscale
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
    
    @staticmethod
    def match_mask_dimensions(
        mask: np.ndarray,
        target_shape: Tuple[int, int]
    ) -> np.ndarray:
        """
        Efficiently resize mask to match target dimensions.
        Uses nearest-neighbor for binary masks (faster).
        
        Args:
            mask: Mask array
            target_shape: (height, width) target shape
            
        Returns:
            Resized mask
        """
        if mask.shape[:2] == target_shape:
            return mask
        
        # Use nearest neighbor for binary masks (faster than LANCZOS)
        return cv2.resize(
            mask,
            (target_shape[1], target_shape[0]),
            interpolation=cv2.INTER_NEAREST
        )
    
    @staticmethod
    def apply_mask_efficient(
        image: np.ndarray,
        mask: np.ndarray,
        overlay: np.ndarray,
        alpha: float = 0.8
    ) -> np.ndarray:
        """
        Efficiently apply overlay to image using mask.
        Vectorized operations for O(n) complexity.
        
        Args:
            image: Base image (H, W, C)
            mask: Binary mask (H, W)
            overlay: Overlay image (H, W, C)
            alpha: Blending factor
            
        Returns:
            Blended image
        """
        # Ensure mask is boolean and matches dimensions
        if mask.shape[:2] != image.shape[:2]:
            mask = ImageOptimizer.match_mask_dimensions(mask, image.shape[:2])
        
        # Normalize mask to [0, 1]
        mask_normalized = (mask > 128).astype(np.float32)
        
        # Expand mask for broadcasting
        if len(image.shape) == 3:
            mask_normalized = mask_normalized[:, :, np.newaxis]
        
        # Vectorized blending (much faster than loops)
        result = (
            alpha * overlay * mask_normalized +
            (1 - alpha) * image * mask_normalized +
            image * (1 - mask_normalized)
        )
        
        return result.astype(np.uint8)
    
    @staticmethod
    def optimize_image_quality(image: np.ndarray) -> np.ndarray:
        """
        Enhance image quality using efficient algorithms.
        
        Args:
            image: Input image
            
        Returns:
            Enhanced image
        """
        # Denoise
        denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        
        # Enhance contrast using CLAHE (efficient)
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced

