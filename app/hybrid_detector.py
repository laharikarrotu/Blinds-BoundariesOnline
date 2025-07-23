import cv2
import numpy as np
from PIL import Image
import os
import requests
import json
import base64
from io import BytesIO

class HybridWindowDetector:
    """
    Hybrid approach: OpenCV (free) + Gemini API (when needed)
    """
    
    def __init__(self, gemini_api_key=None):
        try:
            self.gemini_api_key = gemini_api_key
            self.gemini_available = gemini_api_key is not None
            print(f"✅ Hybrid Window Detector initialized")
            print(f"   - OpenCV: Always available (FREE)")
            print(f"   - Gemini API: {'Available' if self.gemini_available else 'Not configured'}")
        except Exception as e:
            print(f"⚠️ Warning: Error initializing Hybrid Window Detector: {e}")
            self.gemini_api_key = None
            self.gemini_available = False
    
    def detect_windows_opencv(self, image_path, mask_save_path):
        """
        OpenCV-based window detection (FREE)
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("Could not load image")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Create mask
            mask = np.zeros_like(gray)
            
            # Filter contours by area (windows are usually large rectangles)
            min_area = (image.shape[0] * image.shape[1]) * 0.01  # 1% of image
            max_area = (image.shape[0] * image.shape[1]) * 0.8   # 80% of image
            
            window_found = False
            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area < area < max_area:
                    # Approximate contour to polygon
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    # If it's roughly rectangular (4-8 points), it might be a window
                    if 4 <= len(approx) <= 8:
                        # Get bounding rectangle
                        x, y, w, h = cv2.boundingRect(contour)
                        
                        # Check aspect ratio (windows are usually wider than tall)
                        aspect_ratio = w / h
                        if 0.5 < aspect_ratio < 3.0:
                            # Fill the contour in the mask
                            cv2.fillPoly(mask, [contour], 255)
                            window_found = True
            
            # Apply morphological operations to clean up the mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Resize to 320x320 for consistency
            mask_resized = cv2.resize(mask, (320, 320))
            
            # Save the mask
            cv2.imwrite(mask_save_path, mask_resized)
            
            return mask_save_path, window_found
            
        except Exception as e:
            print(f"OpenCV detection error: {e}")
            # Create a simple fallback mask (center rectangle)
            fallback_mask = np.zeros((320, 320), dtype=np.uint8)
            cv2.rectangle(fallback_mask, (80, 80), (240, 240), 255, -1)
            cv2.imwrite(mask_save_path, fallback_mask)
            return mask_save_path, False
    
    def detect_windows_gemini(self, image_path, mask_save_path):
        """
        Gemini API-based window detection (more accurate)
        """
        if not self.gemini_available:
            return None, "Gemini API not configured"
        
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare Gemini API request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={self.gemini_api_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": "Analyze this image and identify all windows. Return a JSON response with the coordinates of each window as bounding boxes in the format: {\"windows\": [{\"x\": 0, \"y\": 0, \"width\": 100, \"height\": 100}]}. Only return the JSON, no other text."
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_data
                            }
                        }
                    ]
                }]
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Make API call
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Parse JSON response
                try:
                    windows_data = json.loads(content)
                    windows = windows_data.get('windows', [])
                    
                    # Create mask from Gemini results
                    image = cv2.imread(image_path)
                    mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
                    
                    for window in windows:
                        x, y, w, h = window['x'], window['y'], window['width'], window['height']
                        cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
                    
                    # Resize to 320x320
                    mask_resized = cv2.resize(mask, (320, 320))
                    cv2.imwrite(mask_save_path, mask_resized)
                    
                    return mask_save_path, len(windows) > 0
                    
                except json.JSONDecodeError:
                    return None, "Failed to parse Gemini response"
            else:
                return None, f"Gemini API error: {response.status_code}"
                
        except Exception as e:
            return None, f"Gemini detection error: {e}"
    
    def detect_window(self, image_path, mask_save_path):
        """
        Main detection method - tries OpenCV first, then Gemini if needed
        """
        print("🔍 Starting hybrid window detection...")
        
        # Try OpenCV first (FREE)
        print("  1. Trying OpenCV detection (FREE)...")
        opencv_result, window_found = self.detect_windows_opencv(image_path, mask_save_path)
        
        # If OpenCV found a window, use it
        if window_found:
            print("  ✅ OpenCV found window - using result (FREE)")
            return opencv_result
        
        # If no window found and Gemini is available, try Gemini
        if self.gemini_available:
            print("  2. OpenCV didn't find window - trying Gemini API...")
            gemini_result, gemini_status = self.detect_windows_gemini(image_path, mask_save_path)
            
            if gemini_result:
                print("  ✅ Gemini found window - using result")
                return gemini_result
            else:
                print(f"  ⚠️ Gemini failed: {gemini_status}")
        
        # Fallback to OpenCV result (even if no window found)
        print("  📋 Using OpenCV result as fallback")
        return opencv_result 