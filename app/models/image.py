"""Image processing models."""
import os
from dataclasses import dataclass
from typing import Optional
from PIL import Image as PILImage
import numpy as np


@dataclass
class ImageData:
    """Image data structure with metadata."""
    image_id: str
    file_path: str
    width: int
    height: int
    format: str
    size_bytes: int
    
    @classmethod
    def from_file(cls, image_id: str, file_path: str) -> 'ImageData':
        """Create ImageData from file."""
        with PILImage.open(file_path) as img:
            return cls(
                image_id=image_id,
                file_path=file_path,
                width=img.width,
                height=img.height,
                format=img.format or "JPEG",
                size_bytes=os.path.getsize(file_path)
            )


@dataclass
class WindowMask:
    """Window mask data structure."""
    mask_path: str
    width: int
    height: int
    coverage_percentage: float
    
    def resize_to_match(self, target_width: int, target_height: int) -> np.ndarray:
        """Resize mask to match target dimensions."""
        from PIL import Image
        mask_img = Image.open(self.mask_path).convert('L')
        mask_img = mask_img.resize((target_width, target_height), Image.LANCZOS)
        return np.array(mask_img)

