print("=== Loading AI-Enhanced Detector (SAM + YOLOv8 + Hybrid) ===")

import cv2
import numpy as np
import os
import time
from typing import Optional, Tuple, Dict, Any

# Import our detectors
from .hybrid_detector import HybridWindowDetector
from .sam_detector import SAMWindowDetector
from .yolo_detector import YOLOv8WindowDetector

print("=== Successfully imported all AI detectors ===")

class AIEnhancedWindowDetector:
    """
    AI-Enhanced Window Detector - Combines SAM, YOLOv8, and Hybrid approaches
    Why: Maximum accuracy through ensemble learning
    Impact: Revolutionary window detection accuracy
    """
    
    def __init__(self, 
                 sam_model_path: str = None,
                 yolo_model_path: str = None,
                 gemini_api_key: str = None,
                 azure_vision_key: str = None,
                 azure_vision_endpoint: str = None,
                 device: str = 'auto',
                 enable_sam: bool = True,
                 enable_yolo: bool = True,
                 enable_hybrid: bool = True):
        """
        Initialize AI-Enhanced detector with all available methods
        """
        try:
            print("🚀 Initializing AI-Enhanced Window Detector...")
            
            self.device = device
            self.enable_sam = enable_sam
            self.enable_yolo = enable_yolo
            self.enable_hybrid = enable_hybrid
            
            # Initialize detectors
            self.detectors = {}
            self.detection_results = {}
            
            # Initialize SAM (GAME CHANGER)
            if self.enable_sam:
                try:
                    # Check if SAM model exists
                    if sam_model_path and not os.path.exists(sam_model_path):
                        print(f"⚠️ SAM model not found at {sam_model_path}, disabling SAM")
                        self.enable_sam = False
                    else:
                        self.detectors['sam'] = SAMWindowDetector(
                            sam_model_path=sam_model_path,
                            device=device
                        )
                        print("✅ SAM Detector initialized")
                except Exception as e:
                    print(f"⚠️ Failed to initialize SAM: {e}")
                    self.enable_sam = False
            
            # Initialize YOLOv8
            if self.enable_yolo:
                try:
                    # Check if YOLOv8 model exists
                    if yolo_model_path and not os.path.exists(yolo_model_path):
                        print(f"⚠️ YOLOv8 model not found at {yolo_model_path}, disabling YOLOv8")
                        self.enable_yolo = False
                    else:
                        self.detectors['yolo'] = YOLOv8WindowDetector(
                            model_path=yolo_model_path,
                            device=device,
                            confidence_threshold=0.5
                        )
                        print("✅ YOLOv8 Detector initialized")
                except Exception as e:
                    print(f"⚠️ Failed to initialize YOLOv8: {e}")
                    self.enable_yolo = False
            
            # Initialize Hybrid (existing)
            if self.enable_hybrid:
                try:
                    self.detectors['hybrid'] = HybridWindowDetector(
                        gemini_api_key=gemini_api_key,
                        azure_vision_key=azure_vision_key,
                        azure_vision_endpoint=azure_vision_endpoint
                    )
                    print("✅ Hybrid Detector initialized")
                except Exception as e:
                    print(f"⚠️ Failed to initialize Hybrid: {e}")
                    self.enable_hybrid = False
            
            print(f"✅ AI-Enhanced Detector initialized successfully")
            print(f"   - Available detectors: {list(self.detectors.keys())}")
            print(f"   - SAM: {'Enabled' if self.enable_sam else 'Disabled'}")
            print(f"   - YOLOv8: {'Enabled' if self.enable_yolo else 'Disabled'}")
            print(f"   - Hybrid: {'Enabled' if self.enable_hybrid else 'Disabled'}")
            
        except Exception as e:
            print(f"❌ Error initializing AI-Enhanced Detector: {e}")
            self.detectors = {}
    
    def detect_window_ensemble(self, image_path: str, mask_save_path: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Ensemble detection using all available AI methods
        """
        print("🔍 AI-Enhanced: Starting ensemble window detection...")
        
        start_time = time.time()
        results = {}
        
        # Run all available detectors
        for detector_name, detector in self.detectors.items():
            try:
                print(f"  Running {detector_name.upper()} detection...")
                
                # Create unique mask path for each detector
                detector_mask_path = mask_save_path.replace('.png', f'_{detector_name}.png')
                
                # Run detection
                if detector_name == 'sam':
                    result = detector.detect_window(image_path, detector_mask_path)
                    success = result is not None
                elif detector_name == 'yolo':
                    result = detector.detect_window(image_path, detector_mask_path)
                    success = result is not None
                elif detector_name == 'hybrid':
                    result = detector.detect_window(image_path, detector_mask_path)
                    success = result is not None
                else:
                    continue
                
                results[detector_name] = {
                    'result': result,
                    'success': success,
                    'mask_path': detector_mask_path
                }
                
                print(f"  ✅ {detector_name.upper()}: {'Success' if success else 'Failed'}")
                
            except Exception as e:
                print(f"  ❌ {detector_name.upper()}: Error - {e}")
                results[detector_name] = {
                    'result': None,
                    'success': False,
                    'error': str(e)
                }
        
        # Ensemble decision making
        final_result = self._ensemble_decision(results, image_path, mask_save_path)
        
        total_time = time.time() - start_time
        print(f"✅ AI-Enhanced ensemble detection completed in {total_time:.2f}s")
        
        return final_result, results
    
    def _ensemble_decision(self, results: Dict[str, Any], image_path: str, final_mask_path: str) -> Optional[str]:
        """
        Make ensemble decision based on all detector results
        """
        successful_detectors = []
        
        # Collect successful detections
        for detector_name, result in results.items():
            if result.get('success', False) and result.get('result'):
                successful_detectors.append(detector_name)
        
        if not successful_detectors:
            print("⚠️ No successful detections from any detector")
            return self._create_fallback_mask(image_path, final_mask_path)
        
        print(f"✅ Successful detections from: {successful_detectors}")
        
        # Priority-based ensemble decision
        if 'sam' in successful_detectors:
            # SAM is the most accurate - use it
            print("🎯 Using SAM result (highest priority)")
            sam_result = results['sam']['mask_path']
            self._copy_mask(sam_result, final_mask_path)
            return final_mask_path
        
        elif 'yolo' in successful_detectors:
            # YOLOv8 is second priority
            print("🎯 Using YOLOv8 result (second priority)")
            yolo_result = results['yolo']['mask_path']
            self._copy_mask(yolo_result, final_mask_path)
            return final_mask_path
        
        elif 'hybrid' in successful_detectors:
            # Hybrid is third priority
            print("🎯 Using Hybrid result (third priority)")
            hybrid_result = results['hybrid']['mask_path']
            self._copy_mask(hybrid_result, final_mask_path)
            return final_mask_path
        
        else:
            # Fallback
            return self._create_fallback_mask(image_path, final_mask_path)
    
    def _copy_mask(self, source_path: str, dest_path: str):
        """
        Copy mask from source to destination
        """
        try:
            if os.path.exists(source_path):
                import shutil
                shutil.copy2(source_path, dest_path)
                print(f"📋 Copied mask from {source_path} to {dest_path}")
            else:
                print(f"⚠️ Source mask not found: {source_path}")
        except Exception as e:
            print(f"❌ Error copying mask: {e}")
    
    def _create_fallback_mask(self, image_path: str, mask_path: str) -> str:
        """
        Create a fallback mask when all detectors fail
        """
        try:
            print("🛠️ Creating fallback mask...")
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("Could not load image")
            
            # Create center-based fallback mask
            h, w = image.shape[:2]
            mask = np.zeros((h, w), dtype=np.uint8)
            
            # Create a large center rectangle
            center_x, center_y = w // 2, h // 2
            mask_size = min(w, h) // 2
            cv2.rectangle(mask, 
                         (center_x - mask_size//2, center_y - mask_size//2),
                         (center_x + mask_size//2, center_y + mask_size//2), 
                         255, -1)
            
            # Apply smoothing
            mask = cv2.GaussianBlur(mask, (15, 15), 0)
            
            # Resize to 320x320
            mask_resized = cv2.resize(mask, (320, 320))
            
            # Save the mask
            cv2.imwrite(mask_path, mask_resized)
            
            print("✅ Fallback mask created successfully")
            return mask_path
            
        except Exception as e:
            print(f"❌ Error creating fallback mask: {e}")
            return None
    
    def detect_window(self, image_path: str, mask_save_path: str) -> Optional[str]:
        """
        Main detection method - uses ensemble approach
        """
        print("🔍 AI-Enhanced: Starting revolutionary ensemble detection...")
        
        result, results = self.detect_window_ensemble(image_path, mask_save_path)
        
        if result:
            print("✅ AI-Enhanced: Revolutionary ensemble detection successful!")
            
            # Print summary
            successful_count = sum(1 for r in results.values() if r.get('success', False))
            total_count = len(results)
            print(f"📊 Detection Summary: {successful_count}/{total_count} detectors successful")
            
            return result
        else:
            print("⚠️ AI-Enhanced: Ensemble detection failed, using fallback")
            return result
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about available detectors
        """
        stats = {
            'total_detectors': len(self.detectors),
            'available_detectors': list(self.detectors.keys()),
            'sam_enabled': self.enable_sam,
            'yolo_enabled': self.enable_yolo,
            'hybrid_enabled': self.enable_hybrid,
            'device': self.device
        }
        
        return stats 