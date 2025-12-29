#!/usr/bin/env python3
"""
Test Azure Computer Vision API connection and configuration.
This script helps diagnose why Azure CV is not responding.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_azure_cv_config():
    """Test Azure Computer Vision configuration."""
    print("=== AZURE COMPUTER VISION DIAGNOSTIC ===")
    print()
    
    # Check environment variables
    print("1. Checking Environment Variables:")
    azure_vision_key = os.getenv("AZURE_VISION_KEY")
    azure_vision_endpoint = os.getenv("AZURE_VISION_ENDPOINT")
    
    print(f"   AZURE_VISION_KEY: {'✅ SET' if azure_vision_key else '❌ NOT SET'}")
    if azure_vision_key:
        print(f"      Length: {len(azure_vision_key)} characters")
        print(f"      First 10 chars: {azure_vision_key[:10]}...")
    else:
        print("      ⚠️ Missing! Set this in Azure App Service or .env file")
    
    print(f"   AZURE_VISION_ENDPOINT: {'✅ SET' if azure_vision_endpoint else '❌ NOT SET'}")
    if azure_vision_endpoint:
        print(f"      Endpoint: {azure_vision_endpoint}")
    else:
        print("      ⚠️ Missing! Set this in Azure App Service or .env file")
    
    print()
    
    # Check config module
    print("2. Checking Config Module:")
    try:
        from app.core.config import config
        print(f"   Config loaded: ✅")
        print(f"   azure_vision_available: {config.azure_vision_available}")
        print(f"   AZURE_VISION_KEY from config: {'✅ SET' if config.AZURE_VISION_KEY else '❌ NOT SET'}")
        print(f"   AZURE_VISION_ENDPOINT from config: {'✅ SET' if config.AZURE_VISION_ENDPOINT else '❌ NOT SET'}")
    except Exception as e:
        print(f"   ❌ Error loading config: {e}")
    
    print()
    
    # Test API call if configured
    if azure_vision_key and azure_vision_endpoint:
        print("3. Testing Azure Computer Vision API:")
        try:
            import requests
            
            # Create a simple test image (1x1 pixel)
            from PIL import Image
            test_image = Image.new('RGB', (100, 100), color='white')
            test_path = project_root / "test_azure_cv.jpg"
            test_image.save(test_path)
            
            # Read image
            with open(test_path, "rb") as f:
                image_data = f.read()
            
            # Test API call
            vision_url = f"{azure_vision_endpoint}/vision/v3.2/analyze"
            headers = {
                'Content-Type': 'application/octet-stream',
                'Ocp-Apim-Subscription-Key': azure_vision_key
            }
            params = {
                'visualFeatures': 'Objects',
                'language': 'en'
            }
            
            print("   Making test API call...")
            response = requests.post(
                vision_url,
                params=params,
                headers=headers,
                data=image_data,
                timeout=10
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅✅✅ SUCCESS! Azure Computer Vision is working!")
                result = response.json()
                print(f"   Objects detected: {len(result.get('objects', []))}")
            elif response.status_code == 401:
                print("   ❌ 401 UNAUTHORIZED - Invalid API key or endpoint")
                print(f"   Response: {response.text[:200]}")
            elif response.status_code == 404:
                print("   ❌ 404 NOT FOUND - Check endpoint URL")
                print(f"   Endpoint: {azure_vision_endpoint}")
            else:
                print(f"   ⚠️ Error {response.status_code}: {response.text[:200]}")
            
            # Cleanup
            test_path.unlink()
            
        except Exception as e:
            print(f"   ❌ API test failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("3. Skipping API test (credentials not configured)")
    
    print()
    print("=== DIAGNOSTIC COMPLETE ===")
    print()
    print("Next Steps:")
    if not azure_vision_key or not azure_vision_endpoint:
        print("1. Get Azure Computer Vision key and endpoint from Azure Portal")
        print("2. Set them in Azure App Service Configuration:")
        print("   - Go to Azure Portal → App Service → Configuration")
        print("   - Add Application Settings:")
        print("     - AZURE_VISION_KEY: <your-key>")
        print("     - AZURE_VISION_ENDPOINT: https://<your-resource>.cognitiveservices.azure.com/")
        print("3. Or set in .env file for local development")
    else:
        print("✅ Credentials are set - check API response above for issues")

if __name__ == "__main__":
    test_azure_cv_config()

