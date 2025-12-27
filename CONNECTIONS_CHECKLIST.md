# Connections Checklist

## 🔴 **REQUIRED CONNECTIONS** (App won't work without these)

### 1. ✅ **Backend Server** (REQUIRED)
- **Status**: ✅ Working (localhost:8000)
- **Check**: `curl http://localhost:8000/health`
- **Action**: None - already working

### 2. ✅ **Frontend Server** (REQUIRED)
- **Status**: ✅ Working (localhost:5173 or 3000)
- **Check**: Open browser to `http://localhost:5173`
- **Action**: None - already working

### 3. ✅ **Backend ↔ Frontend Connection** (REQUIRED)
- **Status**: ⚠️ Check needed
- **Check**: Frontend can call backend API
- **Environment Variable**: 
  ```bash
  # frontend/.env
  VITE_API_BASE_URL=http://localhost:8000
  ```
- **Action**: Ensure frontend can reach backend

---

## 🟡 **OPTIONAL BUT RECOMMENDED** (App works but with limited features)

### 4. **Azure Blob Storage** (OPTIONAL - Recommended for production)
- **Purpose**: Store images in cloud (scalable, fast CDN)
- **Status**: ⚠️ Not configured
- **Required**: 
  - Azure Storage Account
  - Connection String
- **Environment Variable**:
  ```bash
  # Backend .env
  AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net
  AZURE_STORAGE_CONTAINER=window-images
  ```
- **How to Get**:
  1. Go to Azure Portal → Storage Accounts
  2. Create/Select storage account
  3. Go to "Access Keys"
  4. Copy "Connection string"
  5. Create container named "window-images"
- **Check**: `curl http://localhost:8000/health` → `"azure_storage": true`
- **Fallback**: ✅ Works without it (uses local storage)

### 5. **Azure Computer Vision API** (OPTIONAL - Better window detection)
- **Purpose**: AI-powered window detection (most accurate)
- **Status**: ⚠️ Not configured
- **Required**:
  - Azure Computer Vision resource
  - API Key
  - Endpoint URL
- **Environment Variable**:
  ```bash
  # Backend .env
  AZURE_VISION_KEY=your_api_key
  AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
  ```
- **How to Get**:
  1. Go to Azure Portal → Create "Computer Vision" resource
  2. Copy "Key 1" and "Endpoint"
- **Check**: `curl http://localhost:8000/health` → `"azure_vision": true`
- **Fallback**: ✅ Works without it (uses Gemini or OpenCV)

### 6. **Google Gemini API** (OPTIONAL - AI window detection)
- **Purpose**: AI-powered window detection (backup to Azure Vision)
- **Status**: ⚠️ Not configured
- **Required**: Gemini API Key
- **Environment Variable**:
  ```bash
  # Backend .env
  GEMINI_API_KEY=your_gemini_api_key
  ```
- **How to Get**:
  1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
  2. Create API key
  3. Copy key
- **Check**: `curl http://localhost:8000/health` → `"gemini_api": true`
- **Fallback**: ✅ Works without it (uses OpenCV fallback)

---

## 🟢 **OPTIONAL FEATURES** (Not required for core functionality)

### 7. **Auth0** (OPTIONAL - User authentication)
- **Purpose**: User login, favorites, history
- **Status**: ⚠️ Currently disabled
- **Required**:
  - Auth0 account
  - Domain
  - Client ID
- **Environment Variable**:
  ```bash
  # frontend/.env
  VITE_AUTH0_DOMAIN=your-domain.auth0.com
  VITE_AUTH0_CLIENT_ID=your_client_id
  ```
- **How to Get**:
  1. Go to [Auth0.com](https://auth0.com)
  2. Create account
  3. Create Single Page Application
  4. Copy Domain and Client ID
  5. Add callback URLs: `http://localhost:5173`
- **Check**: Login button should work
- **Fallback**: ✅ App works without it (auth features disabled)

### 8. **Firebase** (OPTIONAL - Database for favorites/history)
- **Purpose**: Store user favorites and history
- **Status**: ⚠️ Partially configured (has default values)
- **Required**:
  - Firebase project
  - API Key
  - Project ID
- **Environment Variable**:
  ```bash
  # frontend/.env
  VITE_FIREBASE_API_KEY=your_api_key
  VITE_FIREBASE_PROJECT_ID=your_project_id
  VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
  VITE_FIREBASE_STORAGE_BUCKET=your_project.firebasestorage.app
  ```
- **How to Get**:
  1. Go to [Firebase Console](https://console.firebase.google.com)
  2. Create project
  3. Go to Project Settings → General
  4. Copy config values
- **Check**: Favorites/History features work
- **Fallback**: ✅ App works without it (features disabled)

---

## 📋 **QUICK CHECK COMMANDS**

### Check All Connections:
```bash
# 1. Backend Health (shows all service statuses)
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "components": {
    "detector": true,
    "cache": 0,
    "azure_vision": false,  # true if configured
    "azure_storage": false,  # true if configured
    "gemini_api": false      # true if configured
  }
}

# 2. Frontend API Connection
curl http://localhost:8000/blinds-list

# 3. Test Upload
curl -X POST http://localhost:8000/upload-image -F "file=@test.jpg"
```

---

## 🎯 **PRIORITY ORDER**

### For Development (Local Testing):
1. ✅ Backend Server (port 8000)
2. ✅ Frontend Server (port 5173)
3. ✅ Backend ↔ Frontend connection
4. ⚠️ **That's it!** App works with just these

### For Production (Recommended):
1. ✅ All development connections
2. 🟡 Azure Blob Storage (for scalable storage)
3. 🟡 Azure Computer Vision OR Gemini API (for better detection)
4. 🟢 Auth0 (for user features)
5. 🟢 Firebase (for user data)

---

## 🔧 **SETUP STEPS**

### Step 1: Create Backend .env File
```bash
# Create .env in project root
cat > .env << EOF
# Server
PORT=8000
HOST=0.0.0.0

# Azure Blob Storage (Optional)
AZURE_STORAGE_CONNECTION_STRING=
AZURE_STORAGE_CONTAINER=window-images

# Azure Computer Vision (Optional)
AZURE_VISION_KEY=
AZURE_VISION_ENDPOINT=

# Google Gemini (Optional)
GEMINI_API_KEY=

# Performance
ENABLE_CACHING=true
CACHE_TTL=3600
EOF
```

### Step 2: Create Frontend .env File
```bash
# Create frontend/.env
cd frontend
cat > .env << EOF
# API Connection (REQUIRED)
VITE_API_BASE_URL=http://localhost:8000

# Auth0 (Optional)
VITE_AUTH0_DOMAIN=
VITE_AUTH0_CLIENT_ID=

# Firebase (Optional)
VITE_FIREBASE_API_KEY=
VITE_FIREBASE_PROJECT_ID=
VITE_FIREBASE_AUTH_DOMAIN=
VITE_FIREBASE_STORAGE_BUCKET=
EOF
```

### Step 3: Test Connections
```bash
# Backend
python3 main.py
# Check: http://localhost:8000/health

# Frontend
cd frontend && pnpm dev
# Check: http://localhost:5173
```

---

## ✅ **VERIFICATION CHECKLIST**

- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 5173
- [ ] Frontend can call backend API
- [ ] Health check shows all services
- [ ] Image upload works
- [ ] Window detection works (even with OpenCV fallback)
- [ ] Try-on works
- [ ] (Optional) Azure Blob Storage configured
- [ ] (Optional) Azure Vision or Gemini configured
- [ ] (Optional) Auth0 configured
- [ ] (Optional) Firebase configured

---

## 🚨 **TROUBLESHOOTING**

### Backend not starting?
- Check port 8000 is not in use
- Check Python dependencies: `pip install -r requirements.txt`

### Frontend can't connect to backend?
- Check `VITE_API_BASE_URL` in `frontend/.env`
- Check CORS is enabled in backend
- Check backend is running

### Azure not working?
- Check connection string format
- Check container exists
- Check network access
- **App still works without Azure!**

### AI detection not working?
- Check Azure Vision or Gemini API key
- Check API quotas/limits
- **App still works with OpenCV fallback!**

---

**Summary**: Only 3 connections are REQUIRED (backend, frontend, connection between them). Everything else is optional and has automatic fallbacks!

