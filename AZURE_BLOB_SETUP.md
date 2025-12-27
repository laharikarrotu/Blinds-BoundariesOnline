# Azure Blob Storage Setup Guide

## ✅ **Your Storage Account Details**

- **Account Name**: `blinds-boundaries`
- **Location**: East US
- **Resource Group**: `blinds-boundaries`
- **Account Kind**: StorageV2 (general purpose v2)
- **Blob Anonymous Access**: ✅ Enabled (good for public URLs)
- **Blob Soft Delete**: ✅ Enabled (7 days)

---

## 🔧 **Step 1: Get Connection String**

### Option A: Azure Portal (Easiest)

1. Go to your Storage Account: `blinds-boundaries`
2. Click **"Access Keys"** in the left menu
3. Click **"Show"** next to **"key1"** or **"key2"**
4. Copy the **"Connection string"** (looks like this):
   ```
   DefaultEndpointsProtocol=https;AccountName=blinds-boundaries;AccountKey=...;EndpointSuffix=core.windows.net
   ```

### Option B: Azure CLI
```bash
az storage account show-connection-string \
  --name blinds-boundaries \
  --resource-group blinds-boundaries
```

---

## 📝 **Step 2: Create Container**

### Option A: Azure Portal

1. Go to your Storage Account
2. Click **"Containers"** in the left menu
3. Click **"+ Container"**
4. **Name**: `window-images`
5. **Public access level**: Select **"Blob"** (for public URLs)
6. Click **"Create"**

### Option B: Azure CLI
```bash
az storage container create \
  --name window-images \
  --account-name blinds-boundaries \
  --public-access blob
```

### Option C: Azure Storage Explorer
1. Download [Azure Storage Explorer](https://azure.microsoft.com/features/storage-explorer/)
2. Connect to your account
3. Right-click "Blob Containers" → "Create Blob Container"
4. Name: `window-images`
5. Set public access to "Blob"

---

## 🔑 **Step 3: Configure Backend**

### Create/Update `.env` file in project root:

```bash
# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=blinds-boundaries;AccountKey=YOUR_KEY_HERE;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER=window-images

# Server
PORT=8000
HOST=0.0.0.0
```

**Replace `YOUR_KEY_HERE`** with the actual key from Step 1.

---

## ✅ **Step 4: Test Connection**

### Test via Health Check:
```bash
# Start backend
python3 main.py

# In another terminal, check health
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "components": {
    "azure_storage": true,  // ✅ Should be true
    ...
  }
}
```

### Test Upload:
```bash
# Upload a test image
curl -X POST http://localhost:8000/upload-image \
  -F "file=@test.jpg"
```

**Expected Response:**
```json
{
  "message": "Image uploaded successfully",
  "image_id": "...",
  "azure_url": "https://blinds-boundaries.blob.core.windows.net/window-images/..."  // ✅ Should have Azure URL
}
```

---

## 🔍 **Verify in Azure Portal**

1. Go to Storage Account → **"Containers"** → **"window-images"**
2. You should see uploaded files:
   - `uploads/{image_id}.jpg` - Uploaded images
   - `masks/mask_{image_id}.png` - Generated masks
   - `results/tryon_{image_id}_{blind}.png` - Try-on results

---

## 🎯 **Container Structure**

Your Azure container will have this structure:
```
window-images/
├── uploads/
│   └── {image_id}.jpg
├── masks/
│   └── mask_{image_id}.png
└── results/
    └── tryon_{image_id}_{blind}.png
```

---

## ⚠️ **Important Notes**

1. **Connection String Security**: 
   - Never commit `.env` to git
   - Keep connection string secret
   - Use Azure Key Vault in production

2. **Public Access**:
   - Container is set to "Blob" (public read)
   - URLs will be publicly accessible
   - Good for frontend image display

3. **Soft Delete**:
   - Enabled for 7 days
   - Deleted files can be recovered
   - Good for safety

4. **Costs**:
   - Pay per GB stored
   - Pay per transaction
   - Very cheap for small apps

---

## 🚨 **Troubleshooting**

### Connection String Not Working?
- Check you copied the full string (includes `DefaultEndpointsProtocol=...`)
- Verify account name matches: `blinds-boundaries`
- Check key is correct (no extra spaces)

### Container Not Found?
- Verify container name: `window-images` (exact match)
- Check container exists in Azure Portal
- Ensure public access is set to "Blob"

### Upload Fails?
- Check connection string format
- Verify network access to Azure
- Check Azure account has permissions
- Look at backend logs for errors

### Health Check Shows `azure_storage: false`?
- Verify `.env` file exists in project root
- Check connection string is correct
- Restart backend after updating `.env`

---

## ✅ **Success Checklist**

- [ ] Connection string copied from Azure Portal
- [ ] Container `window-images` created
- [ ] Container public access set to "Blob"
- [ ] `.env` file created with connection string
- [ ] Backend restarted
- [ ] Health check shows `azure_storage: true`
- [ ] Test upload returns `azure_url`

---

**Once configured, all images will automatically upload to Azure!** 🚀

