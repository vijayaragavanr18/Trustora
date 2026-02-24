"""
Main Deepfake Detection Model
Integrates multiple AI/ML models for comprehensive deepfake detection
"""
import asyncio
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# ML imports
import tensorflow as tf
import torch
import cv2
from PIL import Image

# Local imports
# Local imports
try:
    from .config import ModelConfig, AnalysisConfig
    from .models.image_analyzer import ImageAnalyzer
    from .models.video_analyzer import VideoAnalyzer
    from .models.audio_analyzer import AudioAnalyzer
    from .models.model_loader import ModelLoader
except ImportError:
    from config import ModelConfig, AnalysisConfig
    from models.image_analyzer import ImageAnalyzer
    from models.video_analyzer import VideoAnalyzer
    from models.audio_analyzer import AudioAnalyzer
    from models.model_loader import ModelLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepfakeDetector:
    """
    Main class for deepfake detection using ensemble of models
    """
    
    def __init__(self):
        """Initialize all detection models"""
        self.config = ModelConfig()
        self.analysis_config = AnalysisConfig()
        
        logger.info("Initializing Deepfake Detector...")
        
        # Load models
        self.model_loader = ModelLoader()
        self.xception_model = None
        self.efficient_net = None
        self.temporal_transformer = None
        
        # Initialize analyzers
        self.image_analyzer = ImageAnalyzer()
        self.video_analyzer = VideoAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
        
        self._models_loaded = False

    def initialize(self):
        """Initialize and load models synchronously (called on startup)"""
        if self._models_loaded:
            return
        
        logger.info("Pre-loading models on startup...")
        try:
            # Load models synchronously
            logger.info("Loading Xception model...")
            self.xception_model = self.model_loader.load_xception_sync()
            
            logger.info("Loading EfficientNet model...")
            self.efficient_net = self.model_loader.load_efficientnet_sync()
            
            # Temporal is still async/mixed but let's just wait for it if needed or load it sync
            # For now, let's keep it simple as it was
            
            self._models_loaded = True
            logger.info("All models pre-loaded successfully")
        except Exception as e:
            logger.error(f"Failed to pre-load models: {e}")
            # Don't raise here, let it retry on first request if needed
    
    async def load_models(self):
        """Ensure models are loaded (async wrapper)"""
        if self._models_loaded:
            return
            
        # Fallback to sync load if not loaded yet
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.initialize)
    
    async def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze a single image for deepfake artifacts
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with analysis results
        """
        if not self._models_loaded:
            await self.load_models()
        
        try:
            logger.info(f"Analyzing image: {image_path}")
            
            # Load and preprocess image
            loop = asyncio.get_event_loop()
            
            def _load_image():
                img = Image.open(image_path)
                img.load() # ensure loaded
                
                # Resize large images for performance
                max_dim = 1280
                if img.width > max_dim or img.height > max_dim:
                    logger.info(f"Resizing large image from {img.size} to max {max_dim}px")
                    ratio = min(max_dim / img.width, max_dim / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                return img
                
            image = await loop.run_in_executor(None, _load_image)
            image_array = np.array(image)
            
            # Run parallel analysis
            xception_result = await self._analyze_with_xception(image_array)
            efficientnet_result = await self._analyze_with_efficientnet(image_array)
            
            # Additional analyses
            artifacts_analysis = await self.image_analyzer.detect_artifacts(image_array)
            face_boundary_analysis = await self.image_analyzer.analyze_face_boundaries(image_array)
            lighting_analysis = await self.image_analyzer.check_lighting_consistency(image_array)
            metadata_analysis = await self.image_analyzer.detect_metadata_anomalies(image_path)
            
            # Ensemble scoring
            ensemble_score = self._calculate_ensemble_score(
                xception_score=xception_result['score'],
                efficientnet_score=efficientnet_result['score'],
                artifacts_score=artifacts_analysis['score'],
                metadata_score=metadata_analysis['score']
            )
            
            # Generate heatmap
            heatmap_url = await self._generate_heatmap(
                image_array, 
                xception_result.get('attention_map')
            )
            
            # Classify risk
            risk_level = self._classify_risk(ensemble_score)
            
            # Compile artifacts found
            artifacts_found = []
            if artifacts_analysis.get('artifacts_detected'):
                artifacts_found.extend(artifacts_analysis['artifact_types'])
            if face_boundary_analysis.get('anomaly_detected'):
                artifacts_found.append('face_boundary')
            if lighting_analysis.get('inconsistent'):
                artifacts_found.append('lighting')
            if metadata_analysis.get('anomalies'):
                artifacts_found.append('metadata_anomaly')
            
            result = {
                'score': round(ensemble_score, 4),
                'confidence': round(self._calculate_confidence(xception_result, efficientnet_result), 4),
                'risk_level': risk_level,
                'is_deepfake': ensemble_score >= self.analysis_config.DEEPFAKE_THRESHOLD,
                'artifacts_found': artifacts_found,
                'heatmap': heatmap_url,
                'model_scores': {
                    'xception': xception_result['score'],
                    'efficientnet': efficientnet_result['score'],
                    'artifacts': artifacts_analysis['score'],
                    'metadata': metadata_analysis['score']
                },
                'analysis_details': {
                    'face_boundary': face_boundary_analysis,
                    'lighting': lighting_analysis,
                    'metadata': metadata_analysis
                }
            }
            
            logger.info(f"Image analysis complete. Score: {ensemble_score:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            raise

    async def analyze_video(self, video_path: str) -> Dict:
        """Analyze a video file for deepfake artifacts"""
        if not self._models_loaded:
            await self.load_models()
        
        try:
            logger.info(f"Analyzing video: {video_path}")
            
            # 1. Extract frames
            frames = await self.video_analyzer.extract_frames(video_path, fps=2)
            if not frames:
                raise Exception("Could not extract frames from video")
                
            # 2. Frame-by-frame analysis
            frame_scores = []
            for frame in frames[:10]: # Analyze first 10 frames for performance
                res = await self._analyze_frame(frame)
                frame_scores.append(res['score'])
            
            avg_frame_score = np.mean(frame_scores)
            
            # 3. Temporal analysis
            temporal_results = await self.video_analyzer.detect_temporal_inconsistencies(
                frames, self.temporal_transformer
            )
            
            # 4. Audio-visual sync
            sync_results = await self.video_analyzer.check_audio_visual_sync(video_path)
            
            # 5. Motion artifacts
            motion_results = await self.video_analyzer.detect_motion_artifacts(frames)
            
            # 6. Audio analysis (if has audio)
            audio_score = 0.5
            if sync_results.get('has_audio'):
                audio_res = await self.analyze_audio(video_path)
                audio_score = audio_res['score']
            
            # Combine scores
            ensemble_score = self._calculate_video_ensemble_score(
                frame_score=avg_frame_score,
                temporal_score=temporal_results['score'],
                av_sync_score=sync_results['score'],
                motion_score=motion_results['score'],
                audio_score=audio_score
            )
            
            risk_level = self._classify_risk(ensemble_score)
            
            return {
                'score': round(ensemble_score, 4),
                'confidence': round(temporal_results['confidence'], 4),
                'risk_level': risk_level,
                'is_deepfake': ensemble_score >= self.analysis_config.DEEPFAKE_THRESHOLD,
                'artifacts_found': temporal_results.get('anomalies', []) + motion_results.get('artifacts', []),
                'analysis_details': {
                    'temporal': temporal_results,
                    'av_sync': sync_results,
                    'motion': motion_results
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing video: {str(e)}")
            raise

    async def analyze_audio(self, audio_path: str) -> Dict:
        """Analyze an audio file for deepfake artifacts"""
        if not self._models_loaded:
            await self.load_models()
            
        try:
            logger.info(f"Analyzing audio: {audio_path}")
            
            # Use available audio analyzer methods
            spectral = await self.audio_analyzer.spectral_analysis(audio_path)
            synthesis = await self.audio_analyzer.detect_voice_synthesis(audio_path)
            compression = await self.audio_analyzer.detect_compression_artifacts(audio_path)
            
            # Combine scores (weighted)
            ensemble_score = (
                synthesis['score'] * 0.5 +
                spectral['score'] * 0.3 +
                compression['score'] * 0.2
            )
            
            risk_level = self._classify_risk(ensemble_score)
            
            return {
                'score': round(ensemble_score, 4),
                'confidence': round(synthesis['confidence'], 4),
                'risk_level': risk_level,
                'is_deepfake': ensemble_score >= self.analysis_config.DEEPFAKE_THRESHOLD,
                'artifacts_found': ['synthesis'] if synthesis['is_synthetic'] else [],
                'analysis_details': {
                    'spectral': spectral,
                    'synthesis': synthesis,
                    'compression': compression
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing audio: {str(e)}")
            raise

    async def _analyze_with_xception(self, image: np.ndarray) -> Dict:
        """Analyze image with Xception model"""
        loop = asyncio.get_event_loop()
        
        # Run preprocessing and prediction in thread
        def _predict_and_map():
            preprocessed = self.image_analyzer.preprocess_for_xception(image)
            prediction = self.xception_model.predict(preprocessed)
            
            # Generate attention map in the same thread
            attention = None
            try:
                attention = self._get_attention_map(preprocessed, self.xception_model)
            except Exception as e:
                logger.warning(f"Could not generate attention map: {e}")
                
            return prediction, attention

        prediction, attention = await loop.run_in_executor(None, _predict_and_map)
        
        return {
            'score': float(prediction[0][0]),
            'attention_map': attention
        }
    
    async def _analyze_with_efficientnet(self, image: np.ndarray) -> Dict:
        """Analyze image with EfficientNet model"""
        loop = asyncio.get_event_loop()
        
        def _predict():
            preprocessed = self.image_analyzer.preprocess_for_efficientnet(image)
            prediction = self.efficient_net.predict(preprocessed)
            return prediction
            
        prediction = await loop.run_in_executor(None, _predict)
        
        return {
            'score': float(prediction[0][0])
        }
    
    async def _analyze_frame(self, frame: np.ndarray) -> Dict:
        """Analyze single video frame"""
        xception_result = await self._analyze_with_xception(frame)
        efficientnet_result = await self._analyze_with_efficientnet(frame)
        
        frame_score = (
            xception_result['score'] * self.config.XCEPTION_WEIGHT +
            efficientnet_result['score'] * self.config.EFFICIENTNET_WEIGHT
        ) / (self.config.XCEPTION_WEIGHT + self.config.EFFICIENTNET_WEIGHT)
        
        return {'score': frame_score}
    
    def _calculate_ensemble_score(self, xception_score, efficientnet_score, 
                                  artifacts_score, metadata_score) -> float:
        """Calculate weighted ensemble score for image analysis"""
        ensemble = (
            xception_score * self.config.XCEPTION_WEIGHT +
            efficientnet_score * self.config.EFFICIENTNET_WEIGHT +
            artifacts_score * self.config.METADATA_WEIGHT +
            metadata_score * self.config.METADATA_WEIGHT
        )
        return ensemble
    
    def _calculate_video_ensemble_score(self, frame_score, temporal_score, 
                                       av_sync_score, motion_score, audio_score) -> float:
        """Calculate weighted ensemble score for video analysis"""
        ensemble = (
            frame_score * 0.35 +
            temporal_score * self.config.TEMPORAL_WEIGHT +
            av_sync_score * 0.15 +
            motion_score * 0.15 +
            audio_score * self.config.AUDIO_WEIGHT
        )
        return ensemble
    
    def _calculate_confidence(self, result1, result2) -> float:
        """Calculate confidence based on model agreement"""
        score_diff = abs(result1['score'] - result2['score'])
        confidence = 1.0 - (score_diff / 2.0)  # Normalize
        return max(0.0, min(1.0, confidence))
    
    def _classify_risk(self, score: float) -> str:
        """Classify risk level based on score"""
        if score < self.analysis_config.RISK_LOW:
            return "LOW"
        elif score < self.analysis_config.RISK_MEDIUM:
            return "MEDIUM"
        elif score < self.analysis_config.RISK_HIGH:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _get_attention_map(self, image, model):
        """
        Generate Grad-CAM attention map from model.
        Uses the last convolutional layer to see where the model is looking.
        """
        try:
            # We need the last conv layer
            last_conv_layer_name = None
            for layer in reversed(model.layers):
                if 'conv' in layer.name.lower():
                    last_conv_layer_name = layer.name
                    break
            
            if not last_conv_layer_name:
                return None

            # Create a model that maps input to (last_conv_layer, output)
            grad_model = tf.keras.models.Model(
                [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
            )

            # Record operations for automatic differentiation
            with tf.GradientTape() as tape:
                last_conv_layer_output, preds = grad_model(image)
                # For binary classification, we just take the single output
                class_channel = preds[:, 0]

            # Gradient of the prediction with respect to the output of last conv layer
            grads = tape.gradient(class_channel, last_conv_layer_output)

            # Mean intensity of the gradient over each feature map channel
            pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

            # Multiply each channel in last_conv_layer_output by "how important it is"
            last_conv_layer_output = last_conv_layer_output[0]
            heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
            heatmap = tf.squeeze(heatmap)

            # For visualization, we will also normalize the heatmap between 0 & 1
            heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
            return heatmap.numpy()
        except Exception as e:
            logger.warning(f"Grad-CAM generation failed: {e}")
            return None
    
    async def _generate_heatmap(self, image: np.ndarray, heatmap) -> str:
        """
        Process the raw heatmap and overlay it on the original image.
        Saves the result as a JPEG and returns the URL.
        """
        if heatmap is None:
            return None
            
        try:
            import os
            import uuid
            from app.config import settings

            # 1. Resize heatmap to match image size
            heatmap = cv2.resize(heatmap, (image.shape[1], image.shape[0]))

            # 2. Rescale heatmap to 0-255
            heatmap = np.uint8(255 * heatmap)

            # 3. Apply Jet colormap
            heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

            # 4. Superimpose the heatmap on original image
            # Convert original image to BGR for cv2 if it's RGB
            if len(image.shape) == 3:
                img_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                
            superimposed_img = heatmap * 0.4 + img_bgr
            
            # 5. Save the image
            heatmaps_dir = os.path.join(settings.UPLOAD_DIR, "heatmaps")
            if not os.path.exists(heatmaps_dir):
                os.makedirs(heatmaps_dir, exist_ok=True)
                
            filename = f"heatmap_{uuid.uuid4().hex[:8]}.jpg"
            filepath = os.path.join(heatmaps_dir, filename)
            
            cv2.imwrite(filepath, superimposed_img)
            
            # 6. Return the relative URL
            return f"/uploads/heatmaps/{filename}"
            
        except Exception as e:
            logger.error(f"Error saving heatmap: {e}")
            return None


# Singleton instance
_detector_instance = None

def get_detector() -> DeepfakeDetector:
    """Get or create singleton detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = DeepfakeDetector()
    return _detector_instance
