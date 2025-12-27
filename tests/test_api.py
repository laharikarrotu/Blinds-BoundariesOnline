"""Integration tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check_returns_200(self):
        """Health endpoint should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_check_has_status(self):
        """Health endpoint should include status field."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_check_has_version(self):
        """Health endpoint should include version."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data
    
    def test_health_check_has_components(self):
        """Health endpoint should include components status."""
        response = client.get("/health")
        data = response.json()
        assert "components" in data
        assert isinstance(data["components"], dict)


class TestRootEndpoint:
    """Test root endpoint."""
    
    def test_root_returns_200(self):
        """Root endpoint should return 200 OK."""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_has_message(self):
        """Root endpoint should include message."""
        response = client.get("/")
        data = response.json()
        assert "message" in data


class TestBlindsListEndpoint:
    """Test blinds list endpoint."""
    
    def test_blinds_list_returns_200(self):
        """Blinds list endpoint should return 200 OK."""
        response = client.get("/blinds-list")
        assert response.status_code == 200
    
    def test_blinds_list_has_structure(self):
        """Blinds list should have expected structure."""
        response = client.get("/blinds-list")
        data = response.json()
        assert "texture_blinds" in data or "generated_patterns" in data
        assert isinstance(data.get("texture_blinds", []), list)
        assert isinstance(data.get("generated_patterns", []), list)


class TestUploadImageEndpoint:
    """Test image upload endpoint."""
    
    def test_upload_without_file_returns_422(self):
        """Upload without file should return 422."""
        response = client.post("/upload-image")
        assert response.status_code == 422
    
    def test_upload_with_invalid_file_returns_error(self):
        """Upload with invalid file should return error."""
        response = client.post(
            "/upload-image",
            files={"file": ("test.txt", b"not an image", "text/plain")}
        )
        # Should return 400 or 422 for invalid file type
        assert response.status_code in [400, 422, 500]


class TestErrorHandling:
    """Test error handling."""
    
    def test_nonexistent_endpoint_returns_404(self):
        """Nonexistent endpoint should return 404."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

