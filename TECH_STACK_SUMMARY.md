# Tech Stack & Redundant Files

## 🛠️ TECH STACK

### Backend
- **Python 3.9+** + **FastAPI** + **Uvicorn
- **OpenCV** + **Pillow** + **NumPy** + **SciPy** (image processing)
- **Azure Blob Storage** + **Azure Computer Vision**
- **Google Gemini API**
- **Custom LRU Cache** (in-memory, thread-safe)

### Frontend  
- **React 18** + **TypeScript 5.8** + **Vite 5**
- **Tailwind CSS** (styling)
- **Auth0** (auth - currently disabled)
- **Firebase** (database)
- **react-dropzone** (file uploads)

### Architecture (NEW)
- **Layered Architecture**: API → Service → Repository → Model
- **Design Patterns**: Repository, Factory, Strategy, Singleton
- **Data Structures**: LRU Cache (O(1)), Immutable Models
- **Algorithms**: Vectorized operations (O(n))

---

## 🗑️ REDUNDANT FILES (8 files to delete)

### Entry Points (Keep main.py only)
1. ❌ `startup.py` - Duplicate
2. ❌ `app/main.py` - Redundant

### Startup Scripts
3. ❌ `startup.sh` (root)
4. ❌ `app/startup.sh`

### Vite Configs (Keep .ts only)
5. ❌ `frontend/vite.config.js`
6. ❌ `frontend/vite.config.d.ts`

### Package Files (Root - not needed)
7. ❌ `package.json` (root - only has Firebase)
8. ❌ `package-lock.json` (root - using pnpm)

---

## ✅ FILES TO KEEP

### Backend Entry Points
- ✅ `main.py` - Main entry (handles old + new)
- ✅ `app/main_hybrid.py` - Legacy fallback
- ✅ `app/api/main.py` - Elite architecture

### Frontend Config
- ✅ `frontend/vite.config.ts` - TypeScript config
- ✅ `frontend/package.json` - Dependencies
- ✅ `frontend/pnpm-lock.yaml` - Lock file

---

## 📋 CLEANUP COMMANDS

```bash
# Delete redundant files
rm startup.py
rm app/main.py
rm startup.sh
rm app/startup.sh
rm frontend/vite.config.js
rm frontend/vite.config.d.ts
rm package.json
rm package-lock.json
```

---

## 📊 SUMMARY

**Tech Stack**: Python/FastAPI + React/TypeScript + Azure/Vercel
**Architecture**: Elite layered architecture with patterns
**Redundant Files**: 8 files to delete
**Status**: Production-ready elite architecture

