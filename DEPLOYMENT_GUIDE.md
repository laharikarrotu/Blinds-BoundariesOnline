# Complete Deployment Guide

## 🚀 **Deploy Backend, Computer Vision, and Storage**

---

## 📋 **Step 1: Create Computer Vision Resource**

### **Via Azure Portal:**

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"+ Create a resource"**
3. Search for **"Computer Vision"**
4. Click **"Create"**
5. Fill in:
   - **Subscription**: Azure subscription 1
   - **Resource Group**: `blinds-boundaries`
   - **Region**: East US
   - **Name**: `blinds-boundaries-vision` (or your choice)
   - **Pricing Tier**: F0 (Free) or S1 (Standard) - F0 has limits
6. Click **"Review + create"** → **"Create"**
7. Wait for deployment (~2-3 minutes)
8. Go to resource → **"Keys and Endpoint"**
9. Copy:
   - **Key 1**
   - **Endpoint** (URL)

### **Via Azure CLI:**

```bash
# Create Computer Vision resource
az cognitiveservices account create \
  --name blinds-boundaries-vision \
  --resource-group blinds-boundaries \
  --kind ComputerVision \
  --sku F0 \
  --location eastus \
  --subscription e896fa00-e7b8-489b-9e63-a766bb7a8af6

# Get keys and endpoint
az cognitiveservices account keys list \
  --name blinds-boundaries-vision \
  --resource-group blinds-boundaries

az cognitiveservices account show \
  --name blinds-boundaries-vision \
  --resource-group blinds-boundaries \
  --query properties.endpoint
```

---

## 📋 **Step 2: Create App Service Plan & Web App**

### **Via Azure Portal:**

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"+ Create a resource"**
3. Search for **"Web App"**
4. Click **"Create"**
5. Fill in:
   - **Subscription**: Azure subscription 1
   - **Resource Group**: `blinds-boundaries`
   - **Name**: `blinds-boundaries-api` (must be globally unique)
   - **Publish**: Code
   - **Runtime Stack**: Python 3.12
   - **Operating System**: Linux
   - **Region**: East US
   - **App Service Plan**: Create new
     - **Name**: `blinds-boundaries-plan`
     - **SKU**: Free F1 (for testing) or Basic B1 (for production)
6. Click **"Review + create"** → **"Create"**
7. Wait for deployment (~3-5 minutes)

### **Via Azure CLI:**

```bash
# Create App Service Plan
az appservice plan create \
  --name blinds-boundaries-plan \
  --resource-group blinds-boundaries \
  --sku FREE \
  --is-linux \
  --location eastus

# Create Web App
az webapp create \
  --resource-group blinds-boundaries \
  --plan blinds-boundaries-plan \
  --name blinds-boundaries-api \
  --runtime "PYTHON:3.12" \
  --subscription e896fa00-e7b8-489b-9e63-a766bb7a8af6
```

---

## 📋 **Step 3: Configure Environment Variables**

### **In Azure Portal:**

1. Go to App Service: `blinds-boundaries-api`
2. Click **"Configuration"** in left menu
3. Click **"+ New application setting"**
4. Add these variables:

```bash
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=blindsboundaries;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER=window-images
AZURE_VISION_KEY=your_computer_vision_key
AZURE_VISION_ENDPOINT=https://blinds-boundaries-vision.cognitiveservices.azure.com/
PORT=8000
HOST=0.0.0.0
ENABLE_CACHING=true
```

5. Click **"Save"**

### **Get Storage Connection String:**

1. Go to Storage Account: `blindsboundaries`
2. Click **"Access Keys"**
3. Copy **"Connection string"** from key1

---

## 📋 **Step 4: Deploy Backend Code**

### **Option A: GitHub Actions (Recommended - You Already Have This!)**

1. **Verify GitHub Secret:**
   - Go to GitHub repo → Settings → Secrets and variables → Actions
   - Verify `AZUREAPPSERVICE_PUBLISHPROFILE_CCC4DB30401C446B8B09CE2F2265AE23` exists
   - If not, get publish profile from App Service and add it

2. **Get Publish Profile** (if needed):
   - Go to App Service → "Get publish profile"
   - Download file
   - Add content to GitHub Secrets

3. **Deploy:**
   - Push to `main` branch (auto-deploys)
   - Or manually trigger workflow in GitHub Actions

### **Option B: Azure CLI Deployment:**

```bash
# Configure deployment
az webapp config appsettings set \
  --resource-group blinds-boundaries \
  --name blinds-boundaries-api \
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Deploy from local
az webapp up \
  --resource-group blinds-boundaries \
  --name blinds-boundaries-api \
  --runtime "PYTHON:3.12"
```

### **Option C: ZIP Deploy:**

```bash
# Create deployment package
zip -r deploy.zip . -x "*.git*" "node_modules/*" "frontend/*" "__pycache__/*"

# Deploy
az webapp deployment source config-zip \
  --resource-group blinds-boundaries \
  --name blinds-boundaries-api \
  --src deploy.zip
```

---

## 📋 **Step 5: Verify Storage Account**

### **Storage is Already Configured:**
- ✅ Storage Account: `blindsboundaries` exists
- ✅ Container: `window-images` exists
- ✅ Public Access: Enabled

### **Just Need Connection String:**
1. Go to Storage Account → Access Keys
2. Copy connection string
3. Add to App Service environment variables (Step 3)

---

## ✅ **Step 6: Test Deployment**

### **Test Backend:**
```bash
# Health check
curl https://blinds-boundaries-api.azurewebsites.net/health

# Expected response:
{
  "status": "healthy",
  "components": {
    "azure_storage": true,
    "azure_vision": true,
    ...
  }
}
```

### **Test Upload:**
```bash
curl -X POST https://blinds-boundaries-api.azurewebsites.net/upload-image \
  -F "file=@test.jpg"
```

---

## 🎯 **Quick Deployment Checklist**

- [ ] Create Computer Vision resource
- [ ] Get Computer Vision key and endpoint
- [ ] Create App Service Plan
- [ ] Create Web App
- [ ] Get Storage connection string
- [ ] Configure App Service environment variables
- [ ] Deploy backend code (GitHub Actions or manual)
- [ ] Test health endpoint
- [ ] Test upload endpoint
- [ ] Verify all services working

---

## 💰 **Cost Estimate**

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| **App Service** | Free F1 | $0 (limited) |
| **App Service** | Basic B1 | ~$13/month |
| **Computer Vision** | F0 (Free) | $0 (limited) |
| **Computer Vision** | S1 (Standard) | ~$1-5/month |
| **Storage** | Standard_RAGRS | ~$1-5/month |
| **Total (Free tier)** | | ~$1-5/month |
| **Total (Production)** | | ~$15-23/month |

---

## 🚀 **Let's Deploy!**

I'll help you create the resources step by step. Ready to start?

