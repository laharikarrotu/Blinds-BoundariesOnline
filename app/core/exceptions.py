"""Custom exceptions for the application."""
from typing import Optional


class AppException(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, code: str = "GENERAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ImageProcessingError(AppException):
    """Exception raised during image processing."""
    def __init__(self, message: str, code: str = "IMAGE_PROCESSING_ERROR"):
        super().__init__(message, code, 422)


class WindowDetectionError(AppException):
    """Exception raised during window detection."""
    def __init__(self, message: str, code: str = "WINDOW_DETECTION_ERROR"):
        super().__init__(message, code, 422)


class BlindOverlayError(AppException):
    """Exception raised during blind overlay."""
    def __init__(self, message: str, code: str = "BLIND_OVERLAY_ERROR"):
        super().__init__(message, code, 422)


class ValidationError(AppException):
    """Exception raised for validation errors."""
    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        super().__init__(message, code, 400)


class NotFoundError(AppException):
    """Exception raised when resource not found."""
    def __init__(self, message: str, code: str = "NOT_FOUND"):
        super().__init__(message, code, 404)

