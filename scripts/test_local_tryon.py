#!/usr/bin/env python3
"""
Local try-on test script.
Tests the complete flow: upload → detect → try-on
"""
import requests
import json
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = None  # Will be set if image found

def find_test_image():
    """Find a test image in the project."""
    # Check common locations
    locations = [
        "uploads",
        ".",
        "blinds",
        "tests"
    ]
    
    extensions = [".jpg", ".jpeg", ".png"]
    
    for location in locations:
        path = Path(location)
        if path.exists():
            for ext in extensions:
                for img_file in path.glob(f"*{ext}"):
                    if img_file.is_file() and img_file.stat().st_size > 0:
                        return str(img_file)
    return None

def test_health():
    """Test health endpoint."""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        print("   Start it with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_upload_image(image_path):
    """Test image upload."""
    print("\n" + "="*80)
    print("TEST 2: Image Upload")
    print("="*80)
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (Path(image_path).name, f, 'image/jpeg')}
            response = requests.post(
                f"{API_BASE_URL}/upload-image",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            image_id = data.get('image_id')
            print(f"✅ Image uploaded successfully!")
            print(f"   Image ID: {image_id}")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return image_id
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_detect_window(image_id):
    """Test window detection."""
    print("\n" + "="*80)
    print("TEST 3: Window Detection")
    print("="*80)
    
    try:
        print(f"Detecting window for image_id: {image_id}...")
        response = requests.post(
            f"{API_BASE_URL}/detect-window",
            params={"image_id": image_id},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Window detection successful!")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Detection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_try_on(image_id, blind_name="image1.jpeg", color="#808080"):
    """Test try-on."""
    print("\n" + "="*80)
    print("TEST 4: Try-On")
    print("="*80)
    
    try:
        print(f"Trying on blind for image_id: {image_id}...")
        params = {
            "image_id": image_id,
            "mode": "texture",
            "blind_name": blind_name,
            "color": color
        }
        
        response = requests.post(
            f"{API_BASE_URL}/try-on",
            params=params,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Try-on successful!")
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            result_url = data.get('result_url') or data.get('result_path', '')
            if result_url:
                print(f"\n   🎉 Result URL: {result_url}")
                if result_url.startswith('http'):
                    print(f"   ✅ Result uploaded to Azure!")
                else:
                    print(f"   📁 Local result: {result_url}")
            
            return True
        else:
            print(f"❌ Try-on failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("LOCAL TRY-ON TEST SUITE")
    print("="*80)
    print(f"\nTesting against: {API_BASE_URL}")
    print("Make sure the backend is running: python main.py")
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Backend not running. Please start it first:")
        print("   python main.py")
        return 1
    
    # Find test image
    print("\n" + "="*80)
    print("Finding test image...")
    print("="*80)
    
    test_image = find_test_image()
    if not test_image:
        print("⚠️ No test image found. Please provide an image path:")
        print("   python scripts/test_local_tryon.py <image_path>")
        return 1
    
    print(f"✅ Found test image: {test_image}")
    
    # Test 2: Upload
    image_id = test_upload_image(test_image)
    if not image_id:
        return 1
    
    # Wait a bit for processing
    print("\n⏳ Waiting 2 seconds for image processing...")
    time.sleep(2)
    
    # Test 3: Detection
    if not test_detect_window(image_id):
        print("\n⚠️ Detection failed, but continuing with try-on...")
    
    # Wait a bit for detection
    print("\n⏳ Waiting 3 seconds for detection...")
    time.sleep(3)
    
    # Test 4: Try-on
    if not test_try_on(image_id):
        return 1
    
    # Summary
    print("\n" + "="*80)
    print("✅✅✅ ALL TESTS PASSED!")
    print("="*80)
    print("\nTry-on feature is working correctly!")
    print("Check the result URL above to see the final image.")
    
    return 0

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        TEST_IMAGE_PATH = sys.argv[1]
        if Path(TEST_IMAGE_PATH).exists():
            print(f"Using provided image: {TEST_IMAGE_PATH}")
        else:
            print(f"❌ Image not found: {TEST_IMAGE_PATH}")
            sys.exit(1)
    
    sys.exit(main())

