# Existing Resources - Configuration Guide

## ✅ **Great News! You Already Have Everything!**

### **Resources Found:**

1. ✅ **App Service**: `blinds-boundaries-api` (created 29 days ago)
   - Location: Canada Central
   - Status: Exists

2. ✅ **Computer Vision**: `window-detection-model` (created 3 months ago)
   - Location: East US
   - Status: Exists

3. ✅ **Storage Account**: `blindsboundaries` (created 46 minutes ago)
   - Location: East US
   - Status: Active

4. ✅ **Other Resources** (keep these):
   - Key Vault: `blinds-boundaries-kv`
   - Communication Service: `blinds-communications`
   - Email Service: `blinds-boundaries-email`

---

## 🎯 **What We Need to Do**

Since resources already exist, we just need to:

1. ✅ **Configure App Service** - Add environment variables
2. ✅ **Get Computer Vision keys** - From existing resource
3. ✅ **Get Storage connection string** - From existing storage
4. ✅ **Deploy code** - Push to GitHub or manual deploy

---

## 📋 **Step 1: Get Computer Vision Keys**

### **Instructions:**

1. **Go to Computer Vision Resource:**
   - In Azure Portal, search for: `window-detection-model`
   - Click on it

2. **Get Keys:**
   - Click **"Keys and Endpoint"** in left menu
   - Copy **"Key 1"** and **"Endpoint"** (save these!)

**✅ Tell me when you have the keys!**

---

## 📋 **Step 2: Get Storage Connection String**

### **Instructions:**

1. **Go to Storage Account:**
   - Search for: `blindsboundaries`
   - Click on it

2. **Get Connection String:**
   - Click **"Access Keys"** in left menu
   - Click **"Show"** next to **key1**
   - Copy the **"Connection string"** (the long one)

**✅ Tell me when you have the connection string!**

---

## 📋 **Step 3: Configure App Service**

### **Instructions:**

1. **Go to App Service:**
   - Search for: `blinds-boundaries-api`
   - Click on it

2. **Add Environment Variables:**
   - Click **"Configuration"** in left menu
   - Click **"+ New application setting"**
   - Add these (I'll give you exact values once you have the keys):

   **Settings to Add:**
   - `AZURE_STORAGE_CONNECTION_STRING` = (from Step 2)
   - `AZURE_STORAGE_CONTAINER` = `window-images`
   - `AZURE_VISION_KEY` = (from Step 1)
   - `AZURE_VISION_ENDPOINT` = (from Step 1)
   - `PORT` = `8000`
   - `HOST` = `0.0.0.0`
   - `ENABLE_CACHING` = `true`

3. **Save:**
   - Click **"Save"** at the top
   - Click **"Continue"**

**✅ Tell me when Step 3 is done!**

---

## 📋 **Step 4: Configure Python Startup**

### **Instructions:**

1. **Still in App Service Configuration:**
   - Scroll down to **"General settings"**
   - Find **"Startup Command"**
   - Enter: `python main.py`
   - Click **"Save"**

**✅ Tell me when Step 4 is done!**

---

## 📋 **Step 5: Deploy Code**

### **Option A: GitHub Actions (Easiest)**

You already have GitHub Actions configured! Just:

1. **Get Publish Profile** (if needed):
   - In App Service, click **"Get publish profile"** (top bar)
   - Download the file

2. **Add to GitHub Secrets** (if not already there):
   - Go to GitHub repo → Settings → Secrets
   - Add: `AZUREAPPSERVICE_PUBLISHPROFILE_CCC4DB30401C446B8B09CE2F2265AE23`
   - Paste publish profile content

3. **Deploy:**
   - Push to `main` branch (auto-deploys)
   - OR manually trigger workflow

**✅ Tell me which option you prefer!**

---

## 🎯 **Let's Start!**

**First, get the Computer Vision keys from `window-detection-model` resource.**

Tell me when you have:
- Computer Vision Key 1
- Computer Vision Endpoint

Then I'll guide you through the rest! 🚀

