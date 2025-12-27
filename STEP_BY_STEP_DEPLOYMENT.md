# Step-by-Step Deployment Guide (Chat Version)

## 🚀 **Let's Deploy Everything Step by Step!**

---

## **STEP 1: Create Computer Vision Resource** 📸

### **Instructions:**

1. **Open Azure Portal:**
   - Go to: https://portal.azure.com
   - Make sure you're logged in

2. **Create Resource:**
   - Click **"+ Create a resource"** (top left)
   - Search for: **"Computer Vision"**
   - Click on **"Computer Vision"** from Microsoft
   - Click **"Create"**

3. **Fill in Details:**
   - **Subscription**: Azure subscription 1
   - **Resource Group**: `blinds-boundaries` (select existing)
   - **Region**: East US
   - **Name**: `blinds-boundaries-vision`
   - **Pricing Tier**: 
     - Choose **F0 (Free)** for testing (20 calls/min limit)
     - OR **S1 (Standard)** for production (~$1-5/month)

4. **Create:**
   - Click **"Review + create"**
   - Click **"Create"**
   - Wait 2-3 minutes for deployment

5. **Get Keys:**
   - Once created, click **"Go to resource"**
   - Click **"Keys and Endpoint"** in left menu
   - Copy **"Key 1"** and **"Endpoint"** (save these!)

**✅ Tell me when Step 1 is done, and I'll give you Step 2!**

---

## **STEP 2: Create App Service Plan** 📋

### **Instructions:**

1. **Create Resource:**
   - Click **"+ Create a resource"**
   - Search for: **"App Service Plan"**
   - Click **"Create"**

2. **Fill in Details:**
   - **Subscription**: Azure subscription 1
   - **Resource Group**: `blinds-boundaries`
   - **Name**: `blinds-boundaries-plan`
   - **Operating System**: **Linux**
   - **Region**: East US
   - **Pricing Tier**: 
     - **Free F1** (for testing - limited)
     - OR **Basic B1** (for production - ~$13/month)

3. **Create:**
   - Click **"Review + create"**
   - Click **"Create"**
   - Wait 1-2 minutes

**✅ Tell me when Step 2 is done!**

---

## **STEP 3: Create Web App** 🌐

### **Instructions:**

1. **Create Resource:**
   - Click **"+ Create a resource"**
   - Search for: **"Web App"**
   - Click **"Create"**

2. **Fill in Details:**
   - **Subscription**: Azure subscription 1
   - **Resource Group**: `blinds-boundaries`
   - **Name**: `blinds-boundaries-api` (must be globally unique - try adding numbers if taken)
   - **Publish**: Code
   - **Runtime Stack**: Python 3.12
   - **Operating System**: Linux
   - **Region**: East US
   - **App Service Plan**: Select `blinds-boundaries-plan` (the one you just created)

3. **Create:**
   - Click **"Review + create"**
   - Click **"Create"**
   - Wait 3-5 minutes

**✅ Tell me when Step 3 is done!**

---

## **STEP 4: Get Storage Connection String** 💾

### **Instructions:**

1. **Go to Storage Account:**
   - Search for: `blindsboundaries` in top search bar
   - Click on the storage account

2. **Get Connection String:**
   - Click **"Access Keys"** in left menu
   - Click **"Show"** next to **key1**
   - Copy the **"Connection string"** (the long one)
   - Save it somewhere!

**✅ Tell me when you have the connection string!**

---

## **STEP 5: Configure Environment Variables** ⚙️

### **Instructions:**

1. **Go to Web App:**
   - Search for: `blinds-boundaries-api` in top search bar
   - Click on the web app

2. **Add Environment Variables:**
   - Click **"Configuration"** in left menu
   - Click **"+ New application setting"**
   - Add these one by one:

   **Setting 1:**
   - Name: `AZURE_STORAGE_CONNECTION_STRING`
   - Value: (paste the connection string from Step 4)
   - Click **"OK"**

   **Setting 2:**
   - Name: `AZURE_STORAGE_CONTAINER`
   - Value: `window-images`
   - Click **"OK"**

   **Setting 3:**
   - Name: `AZURE_VISION_KEY`
   - Value: (paste Key 1 from Step 1)
   - Click **"OK"**

   **Setting 4:**
   - Name: `AZURE_VISION_ENDPOINT`
   - Value: (paste Endpoint from Step 1)
   - Click **"OK"**

   **Setting 5:**
   - Name: `PORT`
   - Value: `8000`
   - Click **"OK"**

   **Setting 6:**
   - Name: `HOST`
   - Value: `0.0.0.0`
   - Click **"OK"**

3. **Save:**
   - Click **"Save"** at the top
   - Click **"Continue"** to confirm
   - Wait for save to complete

**✅ Tell me when Step 5 is done!**

---

## **STEP 6: Configure Python Startup** 🐍

### **Instructions:**

1. **Still in Web App:**
   - Click **"Configuration"** in left menu
   - Scroll down to **"General settings"**
   - Find **"Startup Command"**
   - Enter: `python main.py`
   - Click **"Save"**

**✅ Tell me when Step 6 is done!**

---

## **STEP 7: Deploy Code** 📦

### **Option A: GitHub Actions (Easiest)**

1. **Get Publish Profile:**
   - In Web App, click **"Get publish profile"** (top bar)
   - Download the file

2. **Add to GitHub:**
   - Go to your GitHub repo
   - Settings → Secrets and variables → Actions
   - Click **"New repository secret"**
   - Name: `AZUREAPPSERVICE_PUBLISHPROFILE_CCC4DB30401C446B8B09CE2F2265AE23`
   - Value: (paste entire content of publish profile file)
   - Click **"Add secret"**

3. **Deploy:**
   - Push to `main` branch (auto-deploys)
   - OR go to Actions tab → Run workflow manually

### **Option B: Manual Deploy**

I'll guide you through this if needed.

**✅ Tell me which option you want to use!**

---

## **STEP 8: Test Deployment** ✅

### **Instructions:**

Once deployed, test:

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
    ...
  }
}
```

---

## 🎯 **Let's Start!**

**Ready for Step 1?** 

Go to Azure Portal and create the Computer Vision resource. Let me know when you're done or if you need help with any step!

