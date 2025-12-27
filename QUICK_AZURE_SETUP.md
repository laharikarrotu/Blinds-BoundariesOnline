# Quick Azure Blob Storage Setup

## 🎯 **Your Storage Account: `blinds-boundaries`**

---

## 📋 **3 Steps to Connect**

### **Step 1: Get Connection String**

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to: **Storage accounts** → **blinds-boundaries**
3. Click **"Access Keys"** in left menu
4. Click **"Show"** next to **key1**
5. Copy the **"Connection string"** (full string)

**It looks like:**
```
DefaultEndpointsProtocol=https;AccountName=blinds-boundaries;AccountKey=...;EndpointSuffix=core.windows.net
```

---

### **Step 2: Create Container**

1. In same Storage Account, click **"Containers"** in left menu
2. Click **"+ Container"**
3. **Name**: `window-images`
4. **Public access level**: Select **"Blob"** (for public URLs)
5. Click **"Create"**

---

### **Step 3: Add to Backend**

Create `.env` file in project root:

```bash
# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=blinds-boundaries;AccountKey=PASTE_YOUR_KEY_HERE;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER=window-images

# Server
PORT=8000
```

**Replace `PASTE_YOUR_KEY_HERE`** with the actual key from Step 1.

---

## ✅ **Test It**

```bash
# 1. Start backend
python3 main.py

# 2. Check health (in another terminal)
curl http://localhost:8000/health

# Should show: "azure_storage": true
```

---

## 🎉 **Done!**

All images will now automatically upload to Azure Blob Storage!

**See `AZURE_BLOB_SETUP.md` for detailed instructions.**

