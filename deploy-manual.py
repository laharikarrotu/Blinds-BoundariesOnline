#!/usr/bin/env python3
"""
Manual Azure Deployment Script
Prepares files for manual deployment through Azure Portal
"""

import os
import zipfile
import shutil

def create_manual_deployment():
    """Create files for manual Azure Portal deployment"""
    print("📦 Creating manual deployment package...")
    
    # Create deployment directory
    deployment_dir = "manual_deployment"
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
    
    # Copy app directory (flattened for Azure)
    if os.path.exists("app"):
        for file in os.listdir("app"):
            if file.endswith(".py"):
                src = os.path.join("app", file)
                dst = os.path.join(deployment_dir, file)
                shutil.copy2(src, dst)
                print(f"✅ Copied app/{file}")
    
    # Copy blinds directory
    if os.path.exists("blinds"):
        blinds_dir = os.path.join(deployment_dir, "blinds")
        shutil.copytree("blinds", blinds_dir)
        print("✅ Copied blinds directory")
    
    # Create necessary directories
    for dir_name in ["uploads", "masks", "results", "models"]:
        os.makedirs(os.path.join(deployment_dir, dir_name), exist_ok=True)
        print(f"✅ Created {dir_name} directory")
    
    # Create zip file for manual upload
    zip_filename = "manual_deployment.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deployment_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deployment_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Created manual deployment package: {zip_filename}")
    print("\n📋 Manual Deployment Instructions:")
    print("1. Go to Azure Portal: https://portal.azure.com")
    print("2. Navigate to your App Service: blinds-boundaries-api")
    print("3. Go to 'Deployment Center'")
    print("4. Choose 'Manual deployment'")
    print("5. Upload the file: manual_deployment.zip")
    print("6. Deploy!")
    
    return zip_filename

if __name__ == "__main__":
    create_manual_deployment() 