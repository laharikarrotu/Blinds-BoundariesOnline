"""Unit tests for repository layer."""
import pytest
from app.repositories.storage_repository import StorageRepository
from app.repositories.image_repository import ImageRepository


class TestStorageRepository:
    """Test storage repository."""
    
    def test_repository_initialization(self):
        """Repository should initialize without errors."""
        repo = StorageRepository()
        assert repo is not None
    
    def test_is_available(self):
        """Repository should report availability."""
        repo = StorageRepository()
        # Should return bool (True if Azure configured, False otherwise)
        assert isinstance(repo.is_available(), bool)


class TestImageRepository:
    """Test image repository."""
    
    def test_repository_initialization(self):
        """Repository should initialize without errors."""
        repo = ImageRepository()
        assert repo is not None

