# Tech Stack & Redundant Files Analysis

## 🛠️ COMPLETE TECH STACK

### Backend
- **Language**: Python 3.9+
- **Framework**: FastAPI 0.100.0+
- **NEW**: Elite Architecture (layered, patterns, caching)
- **Server**: Uvicorn
- **Image Processing**: OpenCV, Pillow, NumPy, SciPy, scikit-image
- **AI/ML**: Azure Computer Vision, Google Gemini
- **Storage**: Azure Blob Storage
- **Cache**: Custom LRU Cache (in-memory)

### Frontend
- **Language**: TypeScript 5.8.3
- **Framework**: React 18.3.1
- **Build Tool**: Vite 5.3.4
- **Styling**: Tailwind CSS 3.4.17
- **Auth**: Auth0 (disabled currently)
- **Database**: Firebase 12.0.0
- **File Upload**: react-dropzone 14.3.8

### Deployment
- **Backend**: Azure App Service
- **Frontend**: Vercel

### Package Managers
- **Backend**: pip
- **Frontend**: pnpm (primary), npm (fallback)

---

## 🗑️ REDUNDANT FILES TO DELETE

### 1. Duplicate Entry Points
- ❌ `startup.py` - Redundant (main.py does this)
- ❌ `app/main.py` - Redundant (main.py handles it)

### 2. Duplicate Startup Scripts
- ❌ `startup.sh` (root) - Not needed
- ❌ `app/startup.sh` - Not needed

### 3. Duplicate Vite Configs
- ❌ `frontend/vite.config.js` - Use .ts version
- ❌ `frontend/vite.config.d.ts` - Not needed

### 4. Unused Package Files
- ❌ `package.json` (root) - Only has Firebase, not used
- ❌ `package-lock.json` (root) - Using pnpm, not npm

### 5. Deployment Files (Keep for Azure)
- ✅ `azure.yaml` - Keep (Azure deployment)
- ✅ `deploy-manual.py` - Keep (deployment script)

**Total redundant files: 8**

---

## 📁 CURRENT FILE STRUCTURE

```
Blinds-BoundariesOnline/
├── app/
│   ├── core/              # ✅ Elite architecture
│   ├── models/            # ✅ Elite architecture
│   ├── repositories/     # ✅ Elite architecture
│   ├── services/         # ✅ Elite architecture
│   ├── algorithms/       # ✅ Elite architecture
│   ├── cache/            # ✅ Elite architecture
│   ├── api/              # ✅ Elite architecture
│   ├── main_hybrid.py    # ✅ Keep (legacy fallback)
│   └── startup.sh        # ❌ DELETE
├── frontend/
│   ├── vite.config.ts    # ✅ Keep
│   ├── vite.config.js    # ❌ DELETE
│   └── vite.config.d.ts  # ❌ DELETE
├── main.py               # ✅ Keep (main entry)
├── startup.py            # ❌ DELETE
├── startup.sh            # ❌ DELETE
├── package.json          # ❌ DELETE (root)
└── package-lock.json     # ❌ DELETE (root)
```

---

## 🎯 RECOMMENDED ACTIONS

1. **Delete redundant files** (8 files)
2. **Keep elite architecture** (new structure)
3. **Keep main.py** (handles both old/new)
4. **Keep app/main_hybrid.py** (fallback)

---

## 📊 TECH STACK SUMMARY

**Backend**: Python + FastAPI + OpenCV + Azure + Custom Cache
**Frontend**: React + TypeScript + Vite + Tailwind + Firebase
**Architecture**: Layered (API → Service → Repository → Model)
**Patterns**: Repository, Factory, Strategy, Singleton
**Performance**: LRU Cache, Vectorized Algorithms, Async I/O

