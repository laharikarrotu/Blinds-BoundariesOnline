// API Configuration
// Use environment variable if set, otherwise detect production vs development
const getApiBaseUrl = () => {
  // If explicitly set via environment variable, use it (HIGHEST PRIORITY)
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // If running on Vercel (production), use Azure backend
  if (import.meta.env.MODE === 'production' || window.location.hostname !== 'localhost') {
    // Actual Azure App Service URL (retrieved from Azure)
    // App Service is in Canada Central region with unique identifier
    return 'https://blinds-boundaries-api-dbewbmh4bjdsc6ht.canadacentral-01.azurewebsites.net';
  }
  
  // Default to localhost for local development
  return 'http://localhost:8000';
};

export const API_BASE_URL = getApiBaseUrl();

// API Endpoints
export const API_ENDPOINTS = {
  UPLOAD_IMAGE: `${API_BASE_URL}/upload-image`,
  BLINDS_LIST: `${API_BASE_URL}/blinds-list`,
  TRY_ON: `${API_BASE_URL}/try-on`,
  DETECT_WINDOW: `${API_BASE_URL}/detect-window`,
  HEALTH: `${API_BASE_URL}/health`,
}; 