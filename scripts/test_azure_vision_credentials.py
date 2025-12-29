#!/usr/bin/env python3
"""
Test Azure Computer Vision credentials with the provided endpoint and key.
"""

import requests
import sys
from pathlib import Path
from PIL import Image

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_azure_vision():
    """Test Azure Computer Vision API with provided credentials."""
    print("=" * 70)
    print("AZURE COMPUTER VISION CREDENTIALS TEST")
    print("=" * 70)
    print()
    
    # Credentials provided
    endpoint = "https://window-detection-model.cognitiveservices.azure.com/"
    key = "DaYUMDwHRQo2pAzQUVyVJrlioWNILc4eUVRMHrta08iCsmKMvBK2JQQJ99BGACYeBjFXJ3w3AAAFACOG2xzp"
    
    print(f"Endpoint: {endpoint}")
    print(f"Key: {key[:10]}...{key[-10:]}")
    print()
    
    # Create test image
    test_image = Image.new('RGB', (100, 100), color='white')
    test_path = project_root / "test_azure_vision.jpg"
    test_image.save(test_path)
    
    # Read image
    with open(test_path, "rb") as f:
        image_data = f.read()
    
    # Test API versions
    api_versions = ['v3.2', 'v4.0']
    
    for api_version in api_versions:
        print(f"Testing API version {api_version}...")
        
        # Construct URL
        endpoint_clean = endpoint.rstrip('/')
        vision_url = f"{endpoint_clean}/vision/{api_version}/analyze"
        
        print(f"  URL: {vision_url}")
        
        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': key
        }
        
        params = {
            'visualFeatures': 'Objects,Description,Tags',
            'language': 'en'
        }
        
        try:
            response = requests.post(
                vision_url,
                params=params,
                headers=headers,
                data=image_data,
                timeout=10
            )
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅✅✅ SUCCESS! API version {api_version} works!")
                result = response.json()
                print(f"  Response keys: {list(result.keys())}")
                return True
            elif response.status_code == 401:
                print(f"  ❌ Authentication failed (401)")
                print(f"  Error: {response.text[:200]}")
            elif response.status_code == 404:
                print(f"  ❌ Resource not found (404)")
                print(f"  Error: {response.text[:200]}")
                print(f"  ⚠️  This API version might not be available")
            else:
                print(f"  ❌ Error: {response.status_code}")
                print(f"  Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
        
        print()
    
    # Cleanup
    if test_path.exists():
        test_path.unlink()
    
    print("=" * 70)
    return False

if __name__ == "__main__":
    success = test_azure_vision()
    sys.exit(0 if success else 1)

