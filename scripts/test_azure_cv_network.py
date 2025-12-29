#!/usr/bin/env python3
"""
Test Azure Computer Vision network connectivity from App Service perspective.
This verifies if network configuration allows Azure CV API calls.
"""

import requests
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_network_connectivity():
    """Test if App Service can reach Azure Computer Vision."""
    print("=" * 70)
    print("AZURE COMPUTER VISION NETWORK CONNECTIVITY TEST")
    print("=" * 70)
    print()
    
    # Get credentials
    from app.core.config import config
    
    if not config.azure_vision_available:
        print("❌ Azure CV credentials not configured")
        print("   Run: python3 scripts/check_azure_config.py")
        return False
    
    endpoint = config.AZURE_VISION_ENDPOINT
    key = config.AZURE_VISION_KEY
    
    print(f"Endpoint: {endpoint}")
    print(f"Key: {'✅ SET' if key else '❌ NOT SET'}")
    print()
    
    # Create test image
    from PIL import Image
    test_image = Image.new('RGB', (100, 100), color='white')
    test_path = project_root / "test_network.jpg"
    test_image.save(test_path)
    
    # Read image
    with open(test_path, "rb") as f:
        image_data = f.read()
    
    # Test API call
    print("Testing network connectivity...")
    print()
    
    vision_url = f"{endpoint}/vision/v3.2/analyze"
    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': key
    }
    params = {
        'visualFeatures': 'Objects',
        'language': 'en'
    }
    
    try:
        print(f"Making request to: {vision_url}")
        response = requests.post(
            vision_url,
            params=params,
            headers=headers,
            data=image_data,
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            print("✅✅✅ NETWORK CONNECTIVITY: SUCCESS!")
            print("   App Service CAN reach Azure Computer Vision")
            print("   Network configuration is CORRECT")
            result = response.json()
            print(f"   Objects detected: {len(result.get('objects', []))}")
            test_path.unlink()
            return True
        elif response.status_code == 401:
            print("⚠️ AUTHENTICATION ERROR (401)")
            print("   Network is OK, but API key might be wrong")
            print(f"   Response: {response.text[:200]}")
            test_path.unlink()
            return False
        elif response.status_code == 403:
            print("❌ FORBIDDEN (403)")
            print("   Network might be blocked by firewall")
            print("   Check Computer Vision resource network settings")
            print(f"   Response: {response.text[:200]}")
            test_path.unlink()
            return False
        else:
            print(f"⚠️ Error {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            test_path.unlink()
            return False
            
    except requests.exceptions.ConnectionError as e:
        print("❌ CONNECTION ERROR")
        print("   Cannot reach Azure Computer Vision endpoint")
        print(f"   Error: {e}")
        print()
        print("Possible causes:")
        print("  1. Network firewall blocking outbound traffic")
        print("  2. Computer Vision resource has network restrictions")
        print("  3. DNS resolution issue")
        test_path.unlink()
        return False
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT")
        print("   Request timed out - network might be slow or blocked")
        test_path.unlink()
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        test_path.unlink()
        return False

if __name__ == "__main__":
    success = test_network_connectivity()
    print()
    print("=" * 70)
    if success:
        print("✅ NETWORK TEST PASSED")
    else:
        print("❌ NETWORK TEST FAILED")
        print("   Check network configuration and firewall rules")
    print("=" * 70)
    sys.exit(0 if success else 1)

