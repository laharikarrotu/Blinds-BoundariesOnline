"""Repository for cloud storage operations (Azure Blob Storage)."""
from typing import Optional
from pathlib import Path
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError

from app.core.config import config
from app.core.logger import logger
from app.core.exceptions import AppException


class StorageRepository:
    """Repository for Azure Blob Storage operations."""
    
    def __init__(self):
        self.connection_string = config.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = config.AZURE_STORAGE_CONTAINER
        self._client: Optional[BlobServiceClient] = None
    
    @property
    def client(self) -> Optional[BlobServiceClient]:
        """Get or create blob service client."""
        if not self.connection_string:
            return None
        
        if self._client is None:
            try:
                self._client = BlobServiceClient.from_connection_string(
                    self.connection_string
                )
            except Exception as e:
                logger.error(f"Failed to create Azure client: {e}")
                return None
        
        return self._client
    
    def is_available(self) -> bool:
        """Check if Azure storage is available."""
        return self.client is not None
    
    def upload_file(self, local_path: str, blob_name: str) -> Optional[str]:
        """
        Upload file to Azure Blob Storage.
        
        Args:
            local_path: Local file path or BytesIO object
            blob_name: Name for blob in storage
            
        Returns:
            Public URL of uploaded blob or None if failed
        """
        if not self.is_available():
            logger.warning("Azure storage not configured, skipping upload")
            return None
        
        try:
            container_client = self.client.get_container_client(self.container_name)
            
            # Ensure container exists
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"Created container: {self.container_name}")
            
            # Upload blob - handle both file path and BytesIO
            if isinstance(local_path, str):
                with open(local_path, "rb") as data:
                    blob_client = container_client.upload_blob(
                        name=blob_name,
                        data=data,
                        overwrite=True
                    )
            else:
                # Assume it's a BytesIO or file-like object
                blob_client = container_client.upload_blob(
                    name=blob_name,
                    data=local_path,
                    overwrite=True
                )
            
            # Generate public URL
            url = f"https://{self.client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
            
            logger.info(f"Uploaded to Azure: {blob_name}")
            return url
            
        except AzureError as e:
            logger.error(f"Azure upload failed: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error uploading to Azure: {e}")
            return None
    
    def download_file(self, blob_name: str, local_path: str) -> bool:
        """
        Download file from Azure Blob Storage.
        
        Args:
            blob_name: Name of blob in storage
            local_path: Local path to save file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)
            
            # Download blob
            with open(local_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            
            logger.info(f"Downloaded from Azure: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Azure download failed: {e}")
            return False
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Delete file from Azure Blob Storage.
        
        Args:
            blob_name: Name of blob to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            
            logger.info(f"Deleted from Azure: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Azure delete failed: {e}")
            return False
    
    def get_file_url(self, blob_name: str) -> Optional[str]:
        """
        Get public URL for a blob.
        
        Args:
            blob_name: Name of blob
            
        Returns:
            Public URL or None
        """
        if not self.is_available():
            return None
        
        return f"https://{self.client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"

