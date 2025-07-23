# Azure Deployment Guide for Blinds & Boundaries API

## Overview

This project uses GitHub Actions to automatically deploy a Python FastAPI application to Azure Web App. The deployment process builds the application, packages it with all necessary dependencies, and deploys it to Azure.

## Architecture

```
GitHub Repository
       ↓
GitHub Actions Workflow
       ↓
Azure Web App Service
       ↓
FastAPI Application (main_hybrid.py)
```

## Workflow Steps

### 1. Build Job (`build`)
- **Checkout**: Downloads the latest code from the main branch
- **Python Setup**: Installs Python 3.12 and upgrades pip/setuptools
- **Dependencies**: Installs all packages from `requirements.txt`
- **Testing**: Runs basic import tests to verify dependencies
- **Packaging**: Creates a deployment package with all necessary files
- **Artifact**: Uploads the package as a GitHub artifact

### 2. Deploy Job (`deploy`)
- **Download**: Retrieves the build artifact
- **Extract**: Unzips the deployment package
- **Azure Login**: Authenticates with Azure using service principal
- **Deploy**: Deploys the application to Azure Web App
- **Verify**: Confirms successful deployment

## Key Files

### Application Files
- `main.py` - Azure App Service entry point
- `app/main_hybrid.py` - Main FastAPI application with window detection
- `app/hybrid_detector.py` - ML model for window detection
- `startup.sh` - Startup script for Azure Web App

### Configuration Files
- `requirements.txt` - Python dependencies
- `.github/workflows/azure-deploy.yml` - GitHub Actions workflow
- `blinds/` - Static blind texture images

## Azure Configuration

### Required Secrets
The following secrets must be configured in your GitHub repository:

1. `AZUREAPPSERVICE_CLIENTID_35AB600D43D74C60ADA2AC4E65A0CE8D` - Azure service principal client ID
2. `AZUREAPPSERVICE_TENANTID_276A866638E34B1B8C84C7D98077FC2B` - Azure tenant ID
3. `AZUREAPPSERVICE_SUBSCRIPTIONID_3005D1EF01714D65931D987B4E4C731A` - Azure subscription ID

### Environment Variables
Configure these in Azure Web App Configuration:

- `AZURE_STORAGE_CONNECTION_STRING` - For blob storage (optional)
- `AZURE_STORAGE_CONTAINER` - Blob container name (default: "window-images")
- `GEMINI_API_KEY` - For Gemini API integration (optional)

## Deployment Package Contents

The deployment package includes:
```
deployment/
├── main.py                 # Azure entry point
├── startup.sh             # Startup script
├── requirements.txt       # Dependencies
├── main_hybrid.py         # Main FastAPI app
├── hybrid_detector.py     # ML detector
├── blinds/                # Blind textures
├── models/                # ML models (if any)
├── uploads/               # Runtime directory
├── masks/                 # Runtime directory
└── results/               # Runtime directory
```

## API Endpoints

Once deployed, your API will be available at:
- **Base URL**: `https://blinds-boundaries-api.azurewebsites.net`
- **Health Check**: `GET /health`
- **Upload Image**: `POST /upload-image`
- **Detect Window**: `POST /detect-window`
- **Try On Blinds**: `POST /try-on`
- **List Blinds**: `GET /blinds-list`

## Troubleshooting

### Common Issues

1. **Import Errors**: Check that all dependencies are in `requirements.txt`
2. **File Not Found**: Ensure all necessary directories are created in the deployment package
3. **Azure Authentication**: Verify all Azure secrets are correctly configured
4. **Startup Failures**: Check the startup script permissions and Azure Web App logs

### Debugging

1. **GitHub Actions Logs**: Check the workflow run logs for build errors
2. **Azure Logs**: Use Azure Portal to view application logs
3. **Health Check**: Test the `/health` endpoint to verify the app is running

## Manual Deployment

If you need to deploy manually:

1. Create a deployment package:
   ```bash
   mkdir deployment
   cp main.py startup.sh requirements.txt deployment/
   cp -r app/* deployment/
   cp -r blinds deployment/
   mkdir -p deployment/{uploads,masks,results}
   chmod +x deployment/startup.sh
   cd deployment && zip -r ../release.zip ./*
   ```

2. Deploy to Azure using Azure CLI or Azure Portal

## Security Considerations

- All Azure credentials are stored as GitHub secrets
- Environment variables are configured in Azure Web App
- CORS is configured for frontend integration
- File uploads are validated for image types only

## Performance Optimization

- Uses `opencv-python-headless` for smaller deployment size
- Static files are served directly by FastAPI
- Azure Blob Storage integration for scalable file storage
- Hybrid detection combines OpenCV and Gemini API for accuracy

## Monitoring

- Health check endpoint for monitoring
- Azure Application Insights can be enabled
- Logs are available in Azure Portal
- GitHub Actions provides deployment status 