# Azure Deployment Guide

## Deploy Backend to Azure App Service

### Prerequisites
- Azure account with subscription
- Azure CLI installed
- Your ML model files (`models/u2netp.pth`)

### Step 1: Prepare Your Code

1. **Ensure all files are in the `app/` directory:**
   ```
   app/
   ├── main.py
   ├── u2net.py
   ├── u2net_inference.py
   ├── requirements.txt
   ├── startup.py
   └── models/
       └── u2netp.pth
   ```

2. **Create a `.env` file in the root with your Azure Storage connection string:**
   ```env
   AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
   AZURE_STORAGE_CONTAINER=window-images
   ```

### Step 2: Deploy to Azure App Service

#### Option A: Using Azure CLI

```bash
# Login to Azure
az login

# Create a resource group
az group create --name blinds-boundaries-rg --location eastus

# Create an App Service plan
az appservice plan create --name blinds-boundaries-plan --resource-group blinds-boundaries-rg --sku B1 --is-linux

# Create the web app
az webapp create --resource-group blinds-boundaries-rg --plan blinds-boundaries-plan --name your-app-name --runtime "PYTHON:3.11"

# Configure environment variables
az webapp config appsettings set --resource-group blinds-boundaries-rg --name your-app-name --settings AZURE_STORAGE_CONNECTION_STRING="your_connection_string"

# Deploy your code
az webapp deployment source config-local-git --resource-group blinds-boundaries-rg --name your-app-name
git remote add azure <git-url-from-previous-command>
git push azure main
```

#### Option B: Using Azure Portal

1. **Go to [Azure Portal](https://portal.azure.com)**
2. **Create a new App Service**
3. **Choose Python 3.11 runtime**
4. **Upload your code or connect to GitHub**
5. **Set environment variables in Configuration**

### Step 3: Configure Environment Variables

In Azure App Service → Configuration → Application settings:

```
AZURE_STORAGE_CONNECTION_STRING = your_azure_storage_connection_string
AZURE_STORAGE_CONTAINER = window-images
```

### Step 4: Update Frontend Configuration

Once deployed, your backend URL will be:
```
https://your-app-name.azurewebsites.net
```

Update your `frontend/.env`:
```env
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_API_URL=https://your-app-name.azurewebsites.net
```

### Step 5: Test Your API

Your API endpoints will be available at:
- `https://your-app-name.azurewebsites.net/`
- `https://your-app-name.azurewebsites.net/upload-image`
- `https://your-app-name.azurewebsites.net/detect-window`
- `https://your-app-name.azurewebsites.net/try-on`
- `https://your-app-name.azurewebsites.net/blinds-list`

## Alternative: Azure Container Instances

For more control, you can containerize your app:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "startup.py"]
```

## Troubleshooting

1. **Model files too large**: Use Azure File Storage or mount the model files
2. **Memory issues**: Upgrade to a larger App Service plan
3. **CORS errors**: Ensure your frontend domain is in the CORS settings
4. **Environment variables**: Check Azure App Service Configuration

## Cost Estimation

- **Basic App Service Plan (B1)**: ~$13/month
- **Azure Blob Storage**: ~$0.02/GB/month
- **Total**: ~$15-20/month for basic usage 