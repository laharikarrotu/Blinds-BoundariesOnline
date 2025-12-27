// API Configuration
// Use environment variable if set, otherwise use localhost for development
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// API Endpoints
export const API_ENDPOINTS = {
  UPLOAD_IMAGE: `${API_BASE_URL}/upload-image`,
  BLINDS_LIST: `${API_BASE_URL}/blinds-list`,
  TRY_ON: `${API_BASE_URL}/try-on`,
  DETECT_WINDOW: `${API_BASE_URL}/detect-window`,
  HEALTH: `${API_BASE_URL}/health`,
}; 