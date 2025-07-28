print("=== Loading hybrid_detector.py ===")

import cv2
import numpy as np
from PIL import Image
import os
import requests
import json
import base64
from io import BytesIO

print("=== Successfully imported all modules in hybrid_detector ===")

class HybridWindowDetector:
    """
    AI-Enhanced Hybrid approach: Azure Computer Vision + Gemini API + OpenCV fallback
    Focus on: AI-powered window detection for maximum accuracy
    """
    
    def __init__(self, gemini_api_key=None, azure_vision_key=None, azure_vision_endpoint=None):
        try:
            self.gemini_api_key = gemini_api_key
            self.gemini_available = gemini_api_key is not None
            
            # Azure Computer Vision setup
            self.azure_vision_key = azure_vision_key
            self.azure_vision_endpoint = azure_vision_endpoint
            self.azure_vision_available = azure_vision_key is not None and azure_vision_endpoint is not None
            
            print(f"✅ AI-Enhanced Hybrid Window Detector initialized")
            print(f"   - Azure Computer Vision: {'Available' if self.azure_vision_available else 'Not configured'}")
            print(f"   - Gemini API: {'Available' if self.gemini_available else 'Not configured'}")
            print(f"   - OpenCV: Always available (FREE fallback)")
        except Exception as e:
            print(f"⚠️ Warning: Error initializing Hybrid Window Detector: {e}")
            self.gemini_api_key = None
            self.gemini_available = False
            self.azure_vision_available = False
    
    def detect_windows_azure_vision(self, image_path, mask_save_path):
        """
        Azure Computer Vision AI-based window detection (MOST ACCURATE)
        """
        if not self.azure_vision_available:
            return None, "Azure Computer Vision not configured"
        
        try:
            # Read image file
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Azure Computer Vision API endpoint
            vision_url = f"{self.azure_vision_endpoint}/vision/v3.2/analyze"
            
            # Parameters for object detection
            params = {
                'visualFeatures': 'Objects,Description',
                'language': 'en',
                'model-version': 'latest'
            }
            
            headers = {
                'Content-Type': 'application/octet-stream',
                'Ocp-Apim-Subscription-Key': self.azure_vision_key
            }
            
            # Make API call
            response = requests.post(vision_url, params=params, headers=headers, data=image_data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Load image for mask creation
                image = cv2.imread(image_path)
                mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
                
                # Look for window-related objects
                window_objects = []
                for obj in result.get('objects', []):
                    # Check if object is window-related
                    object_name = obj.get('object', '').lower()
                    if any(keyword in object_name for keyword in ['window', 'glass', 'pane', 'frame']):
                        window_objects.append(obj)
                
                # If no specific window objects found, look for rectangular objects
                if not window_objects:
                    for obj in result.get('objects', []):
                        # Check for large rectangular objects (likely windows)
                        bbox = obj.get('rectangle', {})
                        if bbox:
                            x = bbox.get('x', 0)
                            y = bbox.get('y', 0)
                            w = bbox.get('w', 0)
                            h = bbox.get('h', 0)
                            
                            # Check if it's a reasonable size for a window
                            area = w * h
                            image_area = image.shape[0] * image.shape[1]
                            if area > image_area * 0.1:  # At least 10% of image
                                window_objects.append(obj)
                
                # Create mask from detected windows
                for obj in window_objects:
                    bbox = obj.get('rectangle', {})
                    if bbox:
                        x = bbox.get('x', 0)
                        y = bbox.get('y', 0)
                        w = bbox.get('w', 0)
                        h = bbox.get('h', 0)
                        
                        # Add some padding to ensure full coverage
                        padding = 10
                        x = max(0, x - padding)
                        y = max(0, y - padding)
                        w = min(image.shape[1] - x, w + 2 * padding)
                        h = min(image.shape[0] - y, h + 2 * padding)
                        
                        cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
                
                # If no objects detected, try semantic analysis
                if np.count_nonzero(mask) < 1000:
                    # Use description to find windows
                    description = result.get('description', {})
                    captions = description.get('captions', [])
                    
                    for caption in captions:
                        text = caption.get('text', '').lower()
                        if 'window' in text or 'glass' in text:
                            # Create a center-based mask if window is mentioned
                            h, w = image.shape[:2]
                            center_x, center_y = w // 2, h // 2
                            mask_size = min(w, h) // 2
                            cv2.rectangle(mask, 
                                        (center_x - mask_size//2, center_y - mask_size//2),
                                        (center_x + mask_size//2, center_y + mask_size//2), 
                                        255, -1)
                            break
                
                # Apply realistic blending preparation
                final_mask = self._prepare_realistic_mask(mask, image.shape)
                
                # Resize to 320x320
                mask_resized = cv2.resize(final_mask, (320, 320))
                cv2.imwrite(mask_save_path, mask_resized)
                
                print(f"Azure Computer Vision detected {len(window_objects)} window objects")
                return mask_save_path, np.count_nonzero(mask_resized) > 1000
                
            else:
                return None, f"Azure Computer Vision API error: {response.status_code}"
                
        except Exception as e:
            return None, f"Azure Computer Vision detection error: {e}"
    
    def detect_windows_opencv(self, image_path, mask_save_path):
        """
        Enhanced OpenCV-based window detection (FREE) - Focus on 4 critical improvements
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("Could not load image")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # IMPROVEMENT 1: Better Edge Detection
            # Use multiple edge detection methods for better results
            edges_combined = self._enhanced_edge_detection(gray)
            
            # IMPROVEMENT 2: Grid Pattern Recognition
            # Detect window frames and grid lines
            window_frames, grid_lines = self._detect_window_grid(gray, edges_combined)
            
            # IMPROVEMENT 3: Full Window Coverage
            # Create mask for the entire window area (including frame)
            full_window_mask = self._create_glass_mask(gray, window_frames, grid_lines)
            
            # IMPROVEMENT 4: Realistic Blending Preparation
            # Prepare mask for realistic blind application
            final_mask = self._prepare_realistic_mask(full_window_mask, image.shape)
            
            # Resize to 320x320 for consistency
            mask_resized = cv2.resize(final_mask, (320, 320))
            
            # Save the mask
            cv2.imwrite(mask_save_path, mask_resized)
            
            print(f"Enhanced window detection completed. Mask saved: {mask_save_path}")
            print(f"Mask size: {mask_resized.shape}, Non-zero pixels: {np.count_nonzero(mask_resized)}")
            
            return mask_save_path, np.count_nonzero(mask_resized) > 1000
            
        except Exception as e:
            print(f"Enhanced OpenCV detection error: {e}")
            # Create a simple fallback mask (center rectangle)
            fallback_mask = np.zeros((320, 320), dtype=np.uint8)
            cv2.rectangle(fallback_mask, (80, 80), (240, 240), 255, -1)
            cv2.imwrite(mask_save_path, fallback_mask)
            return mask_save_path, False
    
    def _enhanced_edge_detection(self, gray):
        """
        IMPROVEMENT 1: Better Edge Detection
        Uses multiple methods to detect window edges more accurately
        """
        # Method 1: Adaptive Canny with different thresholds
        edges1 = cv2.Canny(gray, 30, 100)
        edges2 = cv2.Canny(gray, 50, 150)
        edges3 = cv2.Canny(gray, 20, 80)
        
        # Method 2: Sobel edge detection
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_edges = np.sqrt(sobelx**2 + sobely**2)
        sobel_edges = np.uint8(sobel_edges / sobel_edges.max() * 255)
        
        # Method 3: Laplacian edge detection
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_edges = np.uint8(np.absolute(laplacian))
        
        # Combine all edge detection methods
        edges_combined = cv2.bitwise_or(edges1, edges2)
        edges_combined = cv2.bitwise_or(edges_combined, edges3)
        edges_combined = cv2.bitwise_or(edges_combined, sobel_edges)
        edges_combined = cv2.bitwise_or(edges_combined, laplacian_edges)
        
        # Clean up edges with morphological operations
        kernel = np.ones((2, 2), np.uint8)
        edges_combined = cv2.morphologyEx(edges_combined, cv2.MORPH_CLOSE, kernel)
        
        return edges_combined
    
    def _detect_window_grid(self, gray, edges):
        """
        IMPROVEMENT 2: Grid Pattern Recognition
        Detects window frames and grid lines for multi-pane windows
        """
        # Find horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        
        # Detect horizontal lines
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=2)
        
        # Detect vertical lines
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=2)
        
        # Combine horizontal and vertical lines
        grid_lines = cv2.bitwise_or(horizontal_lines, vertical_lines)
        
        # Find window frame (outer boundary)
        # Use HoughLinesP to detect strong lines
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
        
        window_frames = np.zeros_like(gray)
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(window_frames, (x1, y1), (x2, y2), 255, 2)
        
        return window_frames, grid_lines
    
    def _create_glass_mask(self, gray, window_frames, grid_lines):
        """
        IMPROVEMENT 3: Full Window Coverage
        Creates mask for the entire window area (including frame)
        """
        # Create initial mask from window frames
        frame_mask = window_frames.copy()
        
        # Dilate frame mask to include the entire window area
        kernel = np.ones((10, 10), np.uint8)
        frame_mask = cv2.dilate(frame_mask, kernel, iterations=5)
        
        # Find contours in frame mask
        contours, _ = cv2.findContours(frame_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create full window mask
        full_window_mask = np.zeros_like(gray)
        
        if contours:
            # Find the largest contour (main window area)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Fill the entire window area (including frame)
            cv2.fillPoly(full_window_mask, [largest_contour], 255)
        
        # If no frames detected, try alternative approach for full window detection
        if np.count_nonzero(full_window_mask) < 1000:
            # Use edge detection to find window boundaries
            edges = cv2.Canny(gray, 30, 100)
            
            # Find contours from edges
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find the largest rectangular contour (likely the window)
            largest_area = 0
            best_contour = None
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > largest_area and area > 5000:  # Minimum area threshold
                    # Check if it's roughly rectangular
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.3 < aspect_ratio < 5.0:  # Reasonable aspect ratio for windows
                        largest_area = area
                        best_contour = contour
            
            if best_contour is not None:
                # Fill the entire window area
                cv2.fillPoly(full_window_mask, [best_contour], 255)
        
        return full_window_mask
    
    def _prepare_realistic_mask(self, glass_mask, image_shape):
        """
        IMPROVEMENT 4: Realistic Blending Preparation
        Prepares mask for realistic blind application with proper edges
        """
        # Apply Gaussian blur to create soft edges for realistic blending
        blurred_mask = cv2.GaussianBlur(glass_mask, (5, 5), 0)
        
        # Normalize to 0-255 range
        normalized_mask = cv2.normalize(blurred_mask, None, 0, 255, cv2.NORM_MINMAX)
        
        # Apply slight erosion to avoid bleeding into frame areas
        kernel = np.ones((2, 2), np.uint8)
        final_mask = cv2.erode(normalized_mask, kernel, iterations=1)
        
        return final_mask
    
    def detect_windows_gemini(self, image_path, mask_save_path):
        """
        Enhanced Gemini API-based window detection (more accurate)
        """
        if not self.gemini_available:
            return None, "Gemini API not configured"
        
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Enhanced prompt for full window coverage
            prompt = """
            Analyze this image and identify all windows. 
            For each window, identify the ENTIRE window area (including frame) that should be covered by blinds.
            
            Return a JSON response in this format:
            {
                "windows": [
                    {
                        "full_window": {"x": 0, "y": 0, "width": 100, "height": 100}
                    }
                ]
            }
            
            The full_window should cover the entire window area including the frame, not just individual panes.
            Only return the JSON, no other text.
            """
            
            # Prepare Gemini API request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={self.gemini_api_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
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
                    
                    # Create enhanced mask from Gemini results
                    image = cv2.imread(image_path)
                    mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
                    
                    for window in windows:
                        # Add full window area to mask
                        full_window = window.get('full_window', {})
                        if full_window:
                            x, y, w, h = full_window['x'], full_window['y'], full_window['width'], full_window['height']
                            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
                    
                    # Apply realistic blending preparation
                    final_mask = self._prepare_realistic_mask(mask, image.shape)
                    
                    # Resize to 320x320
                    mask_resized = cv2.resize(final_mask, (320, 320))
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
        Main detection method - tries Azure Computer Vision first (AI), then Gemini, then OpenCV fallback
        """
        print("🔍 Starting AI-enhanced hybrid window detection...")
        
        # Try Azure Computer Vision first (MOST ACCURATE - AI)
        if self.azure_vision_available:
            print("  1. Trying Azure Computer Vision (AI - MOST ACCURATE)...")
            azure_result, azure_status = self.detect_windows_azure_vision(image_path, mask_save_path)
            
            if azure_result:
                print("  ✅ Azure Computer Vision found window - using AI result")
                return azure_result
            else:
                print(f"  ⚠️ Azure Computer Vision failed: {azure_status}")
        
        # Try Gemini API second (AI)
        if self.gemini_available:
            print("  2. Azure Computer Vision didn't find window - trying Gemini API (AI)...")
            gemini_result, gemini_status = self.detect_windows_gemini(image_path, mask_save_path)
            
            if gemini_result:
                print("  ✅ Gemini found window - using AI result")
                return gemini_result
            else:
                print(f"  ⚠️ Gemini failed: {gemini_status}")
        
        # Try enhanced OpenCV as fallback (FREE)
        print("  3. AI methods didn't find window - trying enhanced OpenCV (FREE)...")
        opencv_result, window_found = self.detect_windows_opencv(image_path, mask_save_path)
        
        if window_found:
            print("  ✅ Enhanced OpenCV found window - using result (FREE)")
            return opencv_result
        
        # Final fallback to OpenCV result (even if no window found)
        print("  📋 Using enhanced OpenCV result as final fallback")
        return opencv_result 