#!/bin/bash
# Quick Deployment Commands for Blinds & Boundaries
# Run these commands one by one

# Set variables
SUBSCRIPTION="e896fa00-e7b8-489b-9e63-a766bb7a8af6"
RESOURCE_GROUP="blinds-boundaries"
LOCATION="eastus"

# Set subscription
az account set --subscription $SUBSCRIPTION

echo "🚀 Starting deployment..."

# Step 1: Create Computer Vision Resource
echo "📸 Step 1: Creating Computer Vision resource..."
az cognitiveservices account create \
  --name blinds-boundaries-vision \
  --resource-group $RESOURCE_GROUP \
  --kind ComputerVision \
  --sku F0 \
  --location $LOCATION

echo "✅ Computer Vision created!"

# Get Computer Vision keys
echo "🔑 Getting Computer Vision keys..."
VISION_KEY=$(az cognitiveservices account keys list \
  --name blinds-boundaries-vision \
  --resource-group $RESOURCE_GROUP \
  --query key1 -o tsv)

VISION_ENDPOINT=$(az cognitiveservices account show \
  --name blinds-boundaries-vision \
  --resource-group $RESOURCE_GROUP \
  --query properties.endpoint -o tsv)

echo "Computer Vision Key: $VISION_KEY"
echo "Computer Vision Endpoint: $VISION_ENDPOINT"

# Step 2: Create App Service Plan
echo "📋 Step 2: Creating App Service Plan..."
az appservice plan create \
  --name blinds-boundaries-plan \
  --resource-group $RESOURCE_GROUP \
  --sku FREE \
  --is-linux \
  --location $LOCATION

echo "✅ App Service Plan created!"

# Step 3: Create Web App
echo "🌐 Step 3: Creating Web App..."
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan blinds-boundaries-plan \
  --name blinds-boundaries-api \
  --runtime "PYTHON:3.12"

echo "✅ Web App created!"

# Step 4: Get Storage Connection String
echo "💾 Step 4: Getting Storage connection string..."
STORAGE_CONNECTION=$(az storage account show-connection-string \
  --name blindsboundaries \
  --resource-group $RESOURCE_GROUP \
  --query connectionString -o tsv)

echo "Storage Connection: $STORAGE_CONNECTION"

# Step 5: Configure App Service Environment Variables
echo "⚙️ Step 5: Configuring environment variables..."
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name blinds-boundaries-api \
  --settings \
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION" \
    AZURE_STORAGE_CONTAINER="window-images" \
    AZURE_VISION_KEY="$VISION_KEY" \
    AZURE_VISION_ENDPOINT="$VISION_ENDPOINT" \
    PORT="8000" \
    HOST="0.0.0.0" \
    ENABLE_CACHING="true"

echo "✅ Environment variables configured!"

# Step 6: Configure Python startup
echo "🐍 Step 6: Configuring Python startup..."
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name blinds-boundaries-api \
  --startup-file "python main.py"

echo "✅ Python startup configured!"

echo "🎉 Deployment setup complete!"
echo ""
echo "Next steps:"
echo "1. Deploy code via GitHub Actions (push to main branch)"
echo "2. Or deploy manually using: az webapp deployment source config-zip"
echo ""
echo "Test your deployment:"
echo "curl https://blinds-boundaries-api.azurewebsites.net/health"

