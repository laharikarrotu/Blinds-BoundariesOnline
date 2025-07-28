#!/usr/bin/env python3
"""
Direct Azure Deployment Script
Deploy directly to Azure App Service without GitHub Actions
"""

import os
import subprocess
import zipfile
import shutil
from pathlib import Path

def create_deployment_package():
    """Create a deployment package for Azure"""
    print("📦 Creating deployment package...")
    
    # Create deployment directory
    deployment_dir = "azure_deployment"
    if os.path.exists(deployment_dir):
        shutil.rmtree(deployment_dir)
    os.makedirs(deployment_dir)
    
    # Copy essential files
    files_to_copy = [
        "main.py",
        "startup.py", 
        "requirements.txt",
        "azure.yaml"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, deployment_dir)
            print(f"✅ Copied {file}")
    
    # Copy app directory
    if os.path.exists("app"):
        app_dir = os.path.join(deployment_dir, "app")
        shutil.copytree("app", app_dir)
        print("✅ Copied app directory")
    
    # Copy blinds directory
    if os.path.exists("blinds"):
        blinds_dir = os.path.join(deployment_dir, "blinds")
        shutil.copytree("blinds", blinds_dir)
        print("✅ Copied blinds directory")
    
    # Create necessary directories
    for dir_name in ["uploads", "masks", "results", "models"]:
        os.makedirs(os.path.join(deployment_dir, dir_name), exist_ok=True)
        print(f"✅ Created {dir_name} directory")
    
    # Create zip file
    zip_filename = "azure_deployment.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deployment_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deployment_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Created deployment package: {zip_filename}")
    return zip_filename

def deploy_to_azure(zip_filename):
    """Deploy to Azure using Azure CLI"""
    print("🚀 Deploying to Azure...")
    
    # Check if Azure CLI is installed
    try:
        subprocess.run(["az", "--version"], check=True, capture_output=True)
        print("✅ Azure CLI is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Azure CLI not found. Please install it first:")
        print("   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    
    # Deploy using Azure CLI
    try:
        app_name = "blinds-boundaries-api"
        resource_group = "your-resource-group"  # You'll need to update this
        
        cmd = [
            "az", "webapp", "deployment", "source", "config-zip",
            "--resource-group", resource_group,
            "--name", app_name,
            "--src", zip_filename
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Deployment successful!")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("=== Direct Azure Deployment ===")
    
    # Create deployment package
    zip_filename = create_deployment_package()
    
    # Deploy to Azure
    if deploy_to_azure(zip_filename):
        print("🎉 Deployment completed successfully!")
        print("Your app should be available at:")
        print("https://blinds-boundaries-api-dbewbmh4bjdsc6ht.canadacentral-01.azurewebsites.net")
    else:
        print("❌ Deployment failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 