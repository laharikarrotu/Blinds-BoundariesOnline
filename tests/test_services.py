"""Unit tests for service layer."""
import pytest
from app.core.config import config
from app.services.window_detection_service import WindowDetectionService
from app.services.blind_overlay_service import BlindOverlayService


class TestWindowDetectionService:
    """Test window detection service."""
    
    def test_service_initialization(self):
        """Service should initialize without errors."""
        service = WindowDetectionService()
        assert service is not None
    
    def test_detector_available(self):
        """Detector should be available or None."""
        service = WindowDetectionService()
        # Detector might be None if dependencies not available
        # If detector exists, it should have the detect_window method
        assert service.detector is None or hasattr(service.detector, 'detect_window')


class TestBlindOverlayService:
    """Test blind overlay service."""
    
    def test_service_initialization(self):
        """Service should initialize without errors."""
        service = BlindOverlayService()
        assert service is not None


class TestConfig:
    """Test configuration."""
    
    def test_config_singleton(self):
        """Config should be a singleton."""
        from app.core.config import config
        assert config is not None
        # Config is decorated with @lru_cache(), so it's an instance, not a class
        assert hasattr(config, 'azure_available')
    
    def test_config_has_azure_properties(self):
        """Config should have Azure-related properties."""
        from app.core.config import config
        assert hasattr(config, 'azure_available')
        assert hasattr(config, 'azure_vision_available')
        assert isinstance(config.azure_available, bool)
        assert isinstance(config.azure_vision_available, bool)

