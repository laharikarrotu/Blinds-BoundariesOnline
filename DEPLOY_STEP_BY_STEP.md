# Step-by-Step Deployment Guide

## 🚀 **Deploy Backend, Computer Vision, and Storage**

---

## 📋 **Step 1: Create Computer Vision Resource**

### **Command:**
```bash
az cognitiveservices account create \
  --name blinds-boundaries-vision \
  --resource-group blinds-boundaries \
  --kind ComputerVision \
  --sku F0 \
  --location eastus \
  --subscription e896fa00-e7b8-489b-9e63-a766bb7a8af6
```

**Or via Azure Portal:**
1. Go to Azure Portal → "+ Create a resource"
2. Search "Computer Vision" → Create
3. Fill in:
   - Name: `blinds-boundaries-vision`
   - Resource Group: `blinds-boundaries`
   - Region: East US
   - Pricing: F0 (Free) or S1 (Standard)
4. Create

**Get Keys:**
```bash
# Get key
az cognitiveservices account keys list \
  --name blinds-boundaries-vision \
  --resource-group blinds-boundaries \
  --query key1 -o tsv

# Get endpoint
az cognitiveservices account show \
  --name blinds-boundaries-vision \
  --resource-group blinds-boundaries \
  --query properties.endpoint -o tsv
```

---

## 📋 **Step 2: Create App Service Plan**

### **Command:**
```bash
az appservice plan create \
  --name blinds-boundaries-plan \
  --resource-group blinds-boundaries \
  --sku FREE \
  --is-linux \
  --location eastus \
  --subscription e896fa00-e7b8-489b-9e63-a766bb7a8af6
```

**Or via Azure Portal:**
1. Go to Azure Portal → "+ Create a resource"
2. Search "App Service Plan" → Create
3. Fill in:
   - Resource Group: `blinds-boundaries`
   - Name: `blinds-boundaries-plan`
   - OS: Linux
   - Region: East US
   - Pricing: Free F1 (testing) or Basic B1 (production)
4. Create

---

## 📋 **Step 3: Create Web App**

### **Command:**
```bash
az webapp create \
  --resource-group blinds-boundaries \
  --plan blinds-boundaries-plan \
  --name blinds-boundaries-api \
  --runtime "PYTHON:3.12" \
  --subscription e896fa00-e7b8-489b-9e63-a766bb7a8af6
```

**Or via Azure Portal:**
1. Go to Azure Portal → "+ Create a resource"
2. Search "Web App" → Create
3. Fill in:
   - Resource Group: `blinds-boundaries`
   - Name: `blinds-boundaries-api` (must be unique)
   - Publish: Code
   - Runtime: Python 3.12
   - OS: Linux
   - Region: East US
   - App Service Plan: `blinds-boundaries-plan`
4. Create

---

## 📋 **Step 4: Get Storage Connection String**

### **Command:**
```bash
az storage account show-connection-string \
  --name blindsboundaries \
  --resource-group blinds-boundaries \
  --query connectionString -o tsv
```

**Or via Azure Portal:**
1. Go to Storage Account: `blindsboundaries`
2. Click "Access Keys"
3. Copy "Connection string" from key1

---

## 📋 **Step 5: Configure Environment Variables**

### **Command:**
```bash
# Get values first
STORAGE_CONN=$(az storage account show-connection-string \
  --name blindsboundaries \
  --resource-group blinds-boundaries \
  --query connectionString -o tsv)

VISION_KEY=$(az cognitiveservices account keys list \
  --name blinds-boundaries-vision \
  --resource-group blinds-boundaries \
  --query key1 -o tsv)

VISION_ENDPOINT=$(az cognitiveservices account show \
  --name blinds-boundaries-vision \
  --resource-group blinds-boundaries \
  --query properties.endpoint -o tsv)

# Set environment variables
az webapp config appsettings set \
  --resource-group blinds-boundaries \
  --name blinds-boundaries-api \
  --settings \
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONN" \
    AZURE_STORAGE_CONTAINER="window-images" \
    AZURE_VISION_KEY="$VISION_KEY" \
    AZURE_VISION_ENDPOINT="$VISION_ENDPOINT" \
    PORT="8000" \
    HOST="0.0.0.0" \
    ENABLE_CACHING="true"
```

**Or via Azure Portal:**
1. Go to App Service: `blinds-boundaries-api`
2. Click "Configuration" → "+ New application setting"
3. Add each variable:
   - `AZURE_STORAGE_CONNECTION_STRING`
   - `AZURE_STORAGE_CONTAINER=window-images`
   - `AZURE_VISION_KEY`
   - `AZURE_VISION_ENDPOINT`
   - `PORT=8000`
   - `HOST=0.0.0.0`
4. Save

---

## 📋 **Step 6: Configure Python Startup**

### **Command:**
```bash
az webapp config set \
  --resource-group blinds-boundaries \
  --name blinds-boundaries-api \
  --startup-file "python main.py"
```

---

## 📋 **Step 7: Deploy Code**

### **Option A: GitHub Actions (Recommended)**

You already have this configured! Just:

1. **Get Publish Profile** (if secret doesn't exist):
   ```bash
   # Download publish profile
   az webapp deployment list-publishing-profiles \
     --name blinds-boundaries-api \
     --resource-group blinds-boundaries \
     --xml > publish-profile.xml
   ```
   
2. **Add to GitHub Secrets:**
   - Go to GitHub repo → Settings → Secrets
   - Add secret: `AZUREAPPSERVICE_PUBLISHPROFILE_CCC4DB30401C446B8B09CE2F2265AE23`
   - Paste content from publish-profile.xml

3. **Deploy:**
   - Push to `main` branch (auto-deploys)
   - Or manually trigger workflow

### **Option B: ZIP Deploy**

```bash
# Create deployment package
zip -r deploy.zip . \
  -x "*.git*" "node_modules/*" "frontend/*" \
  "__pycache__/*" "*.pyc" ".env*" "venv/*"

# Deploy
az webapp deployment source config-zip \
  --resource-group blinds-boundaries \
  --name blinds-boundaries-api \
  --src deploy.zip
```

---

## ✅ **Step 8: Test Deployment**

```bash
# Health check
curl https://blinds-boundaries-api.azurewebsites.net/health

# Expected:
{
  "status": "healthy",
  "components": {
    "azure_storage": true,
    "azure_vision": true,
    ...
  }
}
```

---

## 🎯 **Quick All-in-One Script**

I've created `QUICK_DEPLOY_COMMANDS.sh` - run it to deploy everything!

```bash
chmod +x QUICK_DEPLOY_COMMANDS.sh
./QUICK_DEPLOY_COMMANDS.sh
```

---

## 💰 **Cost After Deployment**

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| App Service | Free F1 | $0 |
| Computer Vision | F0 (Free) | $0 |
| Storage | Standard_RAGRS | ~$1-5 |
| **Total** | | **~$1-5/month** |

---

## ✅ **Deployment Checklist**

- [ ] Computer Vision resource created
- [ ] App Service Plan created
- [ ] Web App created
- [ ] Storage connection string obtained
- [ ] Environment variables configured
- [ ] Python startup configured
- [ ] Code deployed
- [ ] Health check passes
- [ ] All services working

---

**Ready to deploy? Let's do it!** 🚀

