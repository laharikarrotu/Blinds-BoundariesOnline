"""Repository for image data access."""
import os
import uuid
from typing import Optional
from pathlib import Path
from io import BytesIO
from app.core.config import config
from app.core.logger import logger
from app.core.exceptions import NotFoundError
from app.models.image import ImageData


class ImageRepository:
    """Repository for image storage operations with Azure Blob Storage support."""
    
    def __init__(self, storage_repo=None):
        """
        Initialize image repository.
        
        Args:
            storage_repo: Optional StorageRepository for Azure Blob Storage
        """
        self.upload_dir = Path(config.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        self.storage_repo = storage_repo
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to Azure Blob Storage (primary) and local (fallback).
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Generated image_id
        """
        image_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix or ".jpg"
        blob_name = f"uploads/{image_id}{file_extension}"
        
        # Try Azure Blob Storage first (scalable)
        if self.storage_repo and self.storage_repo.is_available():
            try:
                # Upload directly to Azure from bytes
                container_client = self.storage_repo.client.get_container_client(
                    self.storage_repo.container_name
                )
                
                # Ensure container exists
                if not container_client.exists():
                    container_client.create_container()
                
                # Upload blob from bytes
                blob_client = container_client.upload_blob(
                    name=blob_name,
                    data=BytesIO(file_content),
                    overwrite=True
                )
                
                logger.info(f"Image {image_id} saved to Azure Blob Storage")
                
                # Also save locally as fallback/cache
                file_path = self.upload_dir / f"{image_id}{file_extension}"
                with open(file_path, "wb") as f:
                    f.write(file_content)
                
                return image_id
            except Exception as e:
                logger.warning(f"Azure upload failed, using local storage: {e}")
        
        # Fallback to local storage
        file_path = self.upload_dir / f"{image_id}{file_extension}"
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return image_id
    
    def get_image_path(self, image_id: str) -> Optional[Path]:
        """
        Get image file path by image_id.
        Downloads from Azure if not found locally.
        
        Args:
            image_id: Image identifier
            
        Returns:
            Path to image file or None if not found
        """
        # Check local first
        for file in self.upload_dir.glob(f"{image_id}.*"):
            if file.exists():
                return file
        
        # Try downloading from Azure
        if self.storage_repo and self.storage_repo.is_available():
            try:
                container_client = self.storage_repo.client.get_container_client(
                    self.storage_repo.container_name
                )
                
                # Try to find blob with this image_id
                for blob in container_client.list_blobs(name_starts_with=f"uploads/{image_id}"):
                    file_extension = Path(blob.name).suffix
                    local_path = self.upload_dir / f"{image_id}{file_extension}"
                    
                    # Download from Azure
                    blob_client = container_client.get_blob_client(blob.name)
                    with open(local_path, "wb") as download_file:
                        download_file.write(blob_client.download_blob().readall())
                    
                    logger.info(f"Downloaded image {image_id} from Azure")
                    return local_path
            except Exception as e:
                logger.warning(f"Failed to download from Azure: {e}")
        
        return None
    
    def get_image_data(self, image_id: str) -> ImageData:
        """
        Get image data by image_id.
        Downloads from Azure if not found locally.
        
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
        Delete image file from both Azure and local storage.
        
        Args:
            image_id: Image identifier
            
        Returns:
            True if deleted, False if not found
        """
        deleted = False
        
        # Delete from Azure
        if self.storage_repo and self.storage_repo.is_available():
            try:
                container_client = self.storage_repo.client.get_container_client(
                    self.storage_repo.container_name
                )
                for blob in container_client.list_blobs(name_starts_with=f"uploads/{image_id}"):
                    blob_client = container_client.get_blob_client(blob.name)
                    blob_client.delete_blob()
                    deleted = True
                    logger.info(f"Deleted image {image_id} from Azure")
            except Exception as e:
                logger.warning(f"Failed to delete from Azure: {e}")
        
        # Delete from local
        image_path = self.get_image_path(image_id)
        if image_path and image_path.exists():
            image_path.unlink()
            deleted = True
        
        return deleted

