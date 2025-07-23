#!/usr/bin/env python3
"""
Manual deployment script for Azure App Service
This bypasses GitHub Actions and deploys directly
"""

import os
import zipfile
import requests
import json
from pathlib import Path

def create_deployment_package():
    """Create a deployment package with all necessary files"""
    print("📦 Creating deployment package...")
    
    # Create zip file
    with zipfile.ZipFile('deployment.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        added_files = set()
        
        # Add root-level files that Azure needs
        root_files = ['main.py', 'startup.py', 'startup.sh', 'requirements.txt']
        for file_name in root_files:
            if os.path.exists(file_name):
                zipf.write(file_name, file_name)
                added_files.add(file_name)
                print(f"  Added root file: {file_name}")
            else:
                print(f"  Warning: {file_name} not found in root")
        
        # Add app directory contents
        app_dir = Path('app')
        if app_dir.exists():
            for file_path in app_dir.rglob('*'):
                if file_path.is_file():
                    # Add file to zip with relative path
                    arcname = file_path.relative_to(app_dir)
                    # Skip if we already added this file from root
                    if str(arcname) not in added_files:
                        zipf.write(file_path, arcname)
                        print(f"  Added app file: {arcname}")
                    else:
                        print(f"  Skipped duplicate: {arcname}")
        
        # Add supporting directories
        support_dirs = ['blinds', 'models', 'uploads', 'masks', 'results']
        for dir_name in support_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(Path('.'))
                        zipf.write(file_path, arcname)
                        print(f"  Added support file: {arcname}")
            else:
                print(f"  Warning: {dir_name} directory not found")
    
    print("✅ Deployment package created: deployment.zip")
    return 'deployment.zip'

def deploy_to_azure(package_path):
    """Deploy to Azure App Service using REST API"""
    print("🚀 Deploying to Azure App Service...")
    
    # Azure App Service deployment URL
    app_name = "blinds-boundaries-api"
    deployment_url = f"https://{app_name}-dbewbmh4bjdsc6ht.scm.canadacentral-01.azurewebsites.net/api/zipdeploy"
    
    # Read the deployment package
    with open(package_path, 'rb') as f:
        package_data = f.read()
    
    # Headers for deployment
    headers = {
        'Content-Type': 'application/zip',
        'Content-Length': str(len(package_data))
    }
    
    try:
        # Make deployment request
        response = requests.post(deployment_url, data=package_data, headers=headers)
        
        if response.status_code == 200:
            print("✅ Deployment successful!")
            print(f"🌐 Your API is available at: https://{app_name}-dbewbmh4bjdsc6ht.canadacentral-01.azurewebsites.net")
        else:
            print(f"❌ Deployment failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Deployment error: {e}")

def main():
    print("🚀 Manual Azure App Service Deployment")
    print("=" * 50)
    
    # Create deployment package
    package_path = create_deployment_package()
    
    # Deploy to Azure
    deploy_to_azure(package_path)
    
    print("\n📋 Next steps:")
    print("1. Check Azure Portal for deployment status")
    print("2. Test your API endpoint")
    print("3. Check logs if there are issues")
    print("4. Verify startup command in Azure is set to: python startup.py")

if __name__ == "__main__":
    main() 