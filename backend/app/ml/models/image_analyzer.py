"""
Image Analysis Pipeline
CNN artifact detection, face boundary analysis, lighting consistency, metadata anomaly detection
"""
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import tensorflow as tf
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Analyzes images for deepfake artifacts"""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def preprocess_for_xception(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for Xception model"""
        from tensorflow.keras.applications.xception import preprocess_input as xception_preprocess
        
        # Resize to target size
        image = cv2.resize(image, (299, 299))
        
        # Normalize to [-1, 1] (Xception preprocessing)
        image = image.astype(np.float32)
        image = xception_preprocess(image)
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        return image
    
    def preprocess_for_efficientnet(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for EfficientNet model"""
        from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess
        
        # Resize to target size
        image = cv2.resize(image, (299, 299))
        
        # Normalize
        image = image.astype(np.float32)
        image = efficientnet_preprocess(image)
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        return image
    
    async def detect_artifacts(self, image: np.ndarray) -> Dict:
        """
        Detect CNN artifacts and compression anomalies
        """
        try:
            artifacts = []
            score = 0.0
            
            # Convert to grayscale for analysis
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Check for JPEG compression artifacts
            jpeg_quality = self._estimate_jpeg_quality(image)
            if jpeg_quality < 85:
                artifacts.append('low_jpeg_quality')
                score += 0.3
            
            # Check for upscaling artifacts
            upscale_score = self._detect_upscaling(image)
            if upscale_score > 0.5:
                artifacts.append('upscaling_detected')
                score += upscale_score * 0.3
            
            # Check for blending artifacts near face boundaries
            blend_score = self._detect_blending_artifacts(image)
            if blend_score > 0.5:
                artifacts.append('blending_artifacts')
                score += blend_score * 0.4
            
            return {
                'artifacts_detected': len(artifacts) > 0,
                'artifact_types': artifacts,
                'score': min(score, 1.0),
                'jpeg_quality': jpeg_quality
            }
            
        except Exception as e:
            logger.error(f"Error detecting artifacts: {str(e)}")
            return {'artifacts_detected': False, 'artifact_types': [], 'score': 0.0}
    
    async def analyze_face_boundaries(self, image: np.ndarray) -> Dict:
        """
        Analyze face boundaries for inconsistencies
        Common in face-swap deepfakes
        """
        try:
            # Convert to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
            
            gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                return {'anomaly_detected': False, 'score': 0.0, 'faces_found': 0}
            
            anomaly_scores = []
            
            for (x, y, w, h) in faces:
                # Extract face region and surrounding area
                padding = 20
                y1, y2 = max(0, y - padding), min(image.shape[0], y + h + padding)
                x1, x2 = max(0, x - padding), min(image.shape[1], x + w + padding)
                
                face_region = rgb_image[y1:y2, x1:x2]
                
                # Analyze edge sharpness at boundary
                edge_score = self._analyze_boundary_edges(face_region, padding)
                anomaly_scores.append(edge_score)
                
                # Analyze color consistency
                color_score = self._analyze_color_consistency(face_region, padding)
                anomaly_scores.append(color_score)
            
            avg_anomaly = np.mean(anomaly_scores) if anomaly_scores else 0.0
            
            return {
                'anomaly_detected': avg_anomaly > 0.6,
                'score': avg_anomaly,
                'faces_found': len(faces),
                'anomaly_scores': anomaly_scores
            }
            
        except Exception as e:
            logger.error(f"Error analyzing face boundaries: {str(e)}")
            return {'anomaly_detected': False, 'score': 0.0}
    
    async def check_lighting_consistency(self, image: np.ndarray) -> Dict:
        """
        Check for lighting inconsistencies
        Deepfakes often have inconsistent lighting
        """
        try:
            # Convert to LAB color space for better lighting analysis
            if len(image.shape) == 3:
                lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            else:
                # Grayscale image
                return {'inconsistent': False, 'score': 0.0}
            
            # Extract L channel (lightness)
            l_channel = lab[:, :, 0]
            
            # Detect faces
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                return {'inconsistent': False, 'score': 0.0, 'reason': 'no_faces'}
            
            # Compare lighting on face vs background
            face_lighting = []
            background_regions = []
            
            for (x, y, w, h) in faces:
                face_light = np.mean(l_channel[y:y+h, x:x+w])
                face_lighting.append(face_light)
                
                # Sample background regions
                if y > 50:  # Top background
                    bg_light = np.mean(l_channel[max(0, y-50):y, x:x+w])
                    background_regions.append(bg_light)
            
            if not background_regions:
                return {'inconsistent': False, 'score': 0.0}
            
            # Calculate variance
            variance = np.var(face_lighting + background_regions)
            
            # High variance indicates inconsistent lighting
            inconsistency_score = min(variance / 1000.0, 1.0)
            
            return {
                'inconsistent': inconsistency_score > 0.6,
                'score': inconsistency_score,
                'variance': float(variance),
                'face_lighting_avg': float(np.mean(face_lighting)),
                'background_lighting_avg': float(np.mean(background_regions))
            }
            
        except Exception as e:
            logger.error(f"Error checking lighting consistency: {str(e)}")
            return {'inconsistent': False, 'score': 0.0}
    
    async def detect_metadata_anomalies(self, image_path: str) -> Dict:
        """
        Detect metadata anomalies that might indicate manipulation
        """
        try:
            image = Image.open(image_path)
            
            # Extract EXIF data
            exif_data = {}
            info = image._getexif()
            
            if info is not None:
                for tag, value in info.items():
                    tag_name = TAGS.get(tag, tag)
                    exif_data[tag_name] = value
            
            anomalies = []
            score = 0.0
            
            # Check for missing expected metadata
            expected_fields = ['DateTime', 'Make', 'Model']
            missing_fields = [field for field in expected_fields if field not in exif_data]
            
            if len(missing_fields) > 1:
                anomalies.append('missing_metadata')
                score += 0.3
            
            # Check for software editing indicators
            if 'Software' in exif_data:
                software = str(exif_data['Software']).lower()
                editing_software = ['photoshop', 'gimp', 'paint.net', 'aftereffects']
                if any(editor in software for editor in editing_software):
                    anomalies.append('editing_software_detected')
                    score += 0.4
            
            # Check for modification date newer than creation date
            if 'DateTime' in exif_data and 'DateTimeOriginal' in exif_data:
                if exif_data['DateTime'] != exif_data['DateTimeOriginal']:
                    anomalies.append('modification_date_mismatch')
                    score += 0.3
            
            return {
                'anomalies': anomalies,
                'score': min(score, 1.0),
                'exif_data': exif_data
            }
            
        except Exception as e:
            logger.error(f"Error detecting metadata anomalies: {str(e)}")
            return {'anomalies': [], 'score': 0.0, 'exif_data': {}}
    
    def _estimate_jpeg_quality(self, image: np.ndarray) -> int:
        """Estimate JPEG quality (simplified)"""
        # This is a simplified estimation
        # In production, use more sophisticated methods
        laplacian_var = cv2.Laplacian(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image, cv2.CV_64F).var()
        
        # Higher variance generally means better quality
        if laplacian_var > 500:
            return 95
        elif laplacian_var > 200:
            return 85
        elif laplacian_var > 100:
            return 75
        else:
            return 60
    
    def _detect_upscaling(self, image: np.ndarray) -> float:
        """Detect if image has been upscaled"""
        # Check for interpolation artifacts
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        
        # Calculate high frequency content
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shift)
        
        # Low high-frequency content suggests upscaling
        high_freq_energy = np.sum(magnitude[magnitude.shape[0]//4:3*magnitude.shape[0]//4, 
                                            magnitude.shape[1]//4:3*magnitude.shape[1]//4])
        total_energy = np.sum(magnitude)
        
        ratio = high_freq_energy / total_energy if total_energy > 0 else 0
        
        # Lower ratio suggests upscaling
        upscale_score = 1.0 - min(ratio * 10, 1.0)
        return upscale_score
    
    def _detect_blending_artifacts(self, image: np.ndarray) -> float:
        """Detect blending artifacts"""
        # Analyze edges for unnatural smoothness
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        edges = cv2.Canny(gray, 100, 200)
        
        # Calculate edge density
        edge_density = np.sum(edges > 0) / edges.size
        
        # Very low edge density might indicate heavy blending
        if edge_density < 0.05:
            return 0.7
        elif edge_density < 0.1:
            return 0.5
        else:
            return 0.2
    
    def _analyze_boundary_edges(self, face_region: np.ndarray, padding: int) -> float:
        """Analyze edge sharpness at face boundary"""
        gray = cv2.cvtColor(face_region, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Focus on boundary area
        boundary_edges = np.concatenate([
            edges[:padding, :].flatten(),
            edges[-padding:, :].flatten(),
            edges[:, :padding].flatten(),
            edges[:, -padding:].flatten()
        ])
        
        # Calculate edge intensity
        boundary_edge_score = np.mean(boundary_edges) / 255.0
        
        # Unnatural smoothness or sharpness indicates manipulation
        if boundary_edge_score < 0.1 or boundary_edge_score > 0.5:
            return 0.7
        return 0.3
    
    def _analyze_color_consistency(self, face_region: np.ndarray, padding: int) -> float:
        """Analyze color consistency at face boundary"""
        # Compare face color with boundary
        face_center = face_region[padding:-padding, padding:-padding]
        boundary = np.concatenate([
            face_region[:padding, :].reshape(-1, 3),
            face_region[-padding:, :].reshape(-1, 3),
            face_region[:, :padding].reshape(-1, 3),
            face_region[:, -padding:].reshape(-1, 3)
        ])
        
        face_mean = np.mean(face_center, axis=(0, 1))
        boundary_mean = np.mean(boundary, axis=0)
        
        # Calculate color difference
        color_diff = np.linalg.norm(face_mean - boundary_mean)
        
        # Large color difference indicates poor blending
        return min(color_diff / 100.0, 1.0)
