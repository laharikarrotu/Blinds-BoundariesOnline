# Quick Connections Guide

## ✅ **REQUIRED** (App won't work without these)

### 1. Backend Server
- **Port**: 8000
- **Start**: `python3 main.py`
- **Check**: `curl http://localhost:8000/health`

### 2. Frontend Server  
- **Port**: 5173 (Vite default)
- **Start**: `cd frontend && pnpm dev`
- **Check**: Open `http://localhost:5173`

### 3. Backend ↔ Frontend Connection
- **File**: `frontend/.env`
- **Required**: `VITE_API_BASE_URL=http://localhost:8000`

---

## 🟡 **OPTIONAL** (App works without, but recommended)

### Azure Blob Storage
- **Why**: Cloud storage, CDN, scalable
- **File**: Backend `.env`
- **Required**: `AZURE_STORAGE_CONNECTION_STRING=...`
- **Get**: Azure Portal → Storage Account → Access Keys

### Azure Computer Vision
- **Why**: Best AI window detection
- **File**: Backend `.env`
- **Required**: `AZURE_VISION_KEY=...` and `AZURE_VISION_ENDPOINT=...`
- **Get**: Azure Portal → Create Computer Vision resource

### Google Gemini API
- **Why**: AI window detection (backup)
- **File**: Backend `.env`
- **Required**: `GEMINI_API_KEY=...`
- **Get**: [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 🟢 **OPTIONAL FEATURES** (Not required)

### Auth0
- **Why**: User login, favorites
- **File**: `frontend/.env`
- **Required**: `VITE_AUTH0_DOMAIN=...` and `VITE_AUTH0_CLIENT_ID=...`
- **Get**: [Auth0.com](https://auth0.com) → Create app

### Firebase
- **Why**: Database for favorites/history
- **File**: `frontend/.env`
- **Required**: Firebase config values
- **Get**: [Firebase Console](https://console.firebase.google.com)

---

## 📝 **MINIMUM SETUP** (Just to run locally)

### Backend `.env`:
```bash
PORT=8000
```

### Frontend `.env`:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

**That's it!** App works with just these 2 files.

---

## 🧪 **TEST CONNECTIONS**

```bash
# 1. Check backend
curl http://localhost:8000/health

# 2. Check frontend
open http://localhost:5173

# 3. Test API
curl http://localhost:8000/blinds-list
```

---

## ✅ **PRIORITY**

1. **Must Have**: Backend + Frontend + Connection
2. **Should Have**: Azure Blob Storage (for production)
3. **Nice to Have**: Azure Vision or Gemini (better detection)
4. **Optional**: Auth0 + Firebase (user features)

**Remember**: Everything except backend/frontend has automatic fallbacks!

