"""Repository for image data access."""
import os
import uuid
from typing import Optional
from pathlib import Path
from app.core.config import config
from app.core.exceptions import NotFoundError
from app.models.image import ImageData


class ImageRepository:
    """Repository for image storage operations."""
    
    def __init__(self):
        self.upload_dir = Path(config.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file and return image_id.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Generated image_id
        """
        image_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix or ".jpg"
        file_path = self.upload_dir / f"{image_id}{file_extension}"
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return image_id
    
    def get_image_path(self, image_id: str) -> Optional[Path]:
        """
        Get image file path by image_id.
        
        Args:
            image_id: Image identifier
            
        Returns:
            Path to image file or None if not found
        """
        for file in self.upload_dir.glob(f"{image_id}.*"):
            if file.exists():
                return file
        return None
    
    def get_image_data(self, image_id: str) -> ImageData:
        """
        Get image data by image_id.
        
        Args:
            image_id: Image identifier
            
        Returns:
            ImageData object
            
        Raises:
            NotFoundError: If image not found
        """
        image_path = self.get_image_path(image_id)
        if not image_path or not image_path.exists():
            raise NotFoundError(f"Image {image_id} not found")
        
        return ImageData.from_file(image_id, str(image_path))
    
    def delete_image(self, image_id: str) -> bool:
        """
        Delete image file.
        
        Args:
            image_id: Image identifier
            
        Returns:
            True if deleted, False if not found
        """
        image_path = self.get_image_path(image_id)
        if image_path and image_path.exists():
            image_path.unlink()
            return True
        return False

