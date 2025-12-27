# Step 5: Deploy Code to App Service

## 🚀 **Deploy Your Backend Code**

You have 2 options. Let's use the easiest one!

---

## **Option A: GitHub Actions (Recommended - Auto Deploy)**

### **Step 1: Get Publish Profile**

1. **In Azure Portal:**
   - Go to App Service: `blinds-boundaries-api`
   - Click **"Get publish profile"** (top bar, next to Overview)
   - Download the `.PublishSettings` file
   - Open the file in a text editor
   - Copy the entire content

### **Step 2: Add to GitHub Secrets**

1. **Go to GitHub:**
   - Open your repository on GitHub
   - Click **"Settings"** (top menu)
   - Click **"Secrets and variables"** → **"Actions"**
   - Click **"New repository secret"**

2. **Add Secret:**
   - **Name**: `AZUREAPPSERVICE_PUBLISHPROFILE_CCC4DB30401C446B8B09CE2F2265AE23`
   - **Value**: (Paste the entire content from publish profile file)
   - Click **"Add secret"**

### **Step 3: Deploy**

**Option 1: Auto Deploy (Push to main)**
```bash
git add .
git commit -m "Configure App Service environment variables"
git push origin main
```
This will automatically trigger GitHub Actions and deploy!

**Option 2: Manual Trigger**
- Go to GitHub repo → **"Actions"** tab
- Select **"Build and deploy Python app to Azure Web App"**
- Click **"Run workflow"** → **"Run workflow"**

---

## **Option B: Manual ZIP Deploy**

If GitHub Actions doesn't work, we can deploy manually:

1. **Create deployment package:**
```bash
zip -r deploy.zip . \
  -x "*.git*" "node_modules/*" "frontend/*" \
  "__pycache__/*" "*.pyc" ".env*" "venv/*" \
  "*.md" "*.sh"
```

2. **Deploy:**
```bash
az webapp deployment source config-zip \
  --resource-group blinds-boundaries \
  --name blinds-boundaries-api \
  --src deploy.zip
```

---

## ✅ **After Deployment: Test It!**

Once deployed, test your backend:

```bash
curl https://blinds-boundaries-api.azurewebsites.net/health
```

Or open in browser:
https://blinds-boundaries-api.azurewebsites.net/health

**Expected response:**
```json
{
  "status": "healthy",
  "components": {
    "azure_storage": true,
    "azure_vision": true,
    "gemini_api": false,
    ...
  }
}
```

---

## 🎯 **Which Option Do You Want?**

**Option A (GitHub Actions)** is recommended - it's automatic and easier!

Tell me which option you want to use, and I'll guide you through it! 🚀

