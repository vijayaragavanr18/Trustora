"""
Video Analysis Pipeline
Frame extraction, temporal inconsistency detection, audio-visual sync, motion artifacts
"""
import cv2
import numpy as np
import torch
from typing import List, Dict, Tuple
import logging
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """Analyzes videos for deepfake artifacts"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Video analyzer using device: {self.device}")
    
    async def extract_frames(self, video_path: str, fps: int = 5, max_frames: int = 100) -> List[np.ndarray]:
        """
        Extract frames from video at specified FPS
        
        Args:
            video_path: Path to video file
            fps: Frames per second to extract
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of frame arrays
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")
            
            # Get video properties
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Video FPS: {original_fps}, Total frames: {total_frames}")
            
            # Calculate frame interval
            frame_interval = int(original_fps / fps) if fps < original_fps else 1
            
            frames = []
            frame_count = 0
            extracted_count = 0
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
                    extracted_count += 1
                    
                    if extracted_count >= max_frames:
                        break
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Extracted {len(frames)} frames from video")
            
            return frames
            
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
            raise
    
    async def detect_temporal_inconsistencies(self, frames: List[np.ndarray], temporal_model) -> Dict:
        """
        Detect temporal inconsistencies using temporal transformer
        Deepfakes often have frame-to-frame inconsistencies
        
        Args:
            frames: List of video frames
            temporal_model: Trained temporal transformer model
            
        Returns:
            Dictionary with temporal analysis results
        """
        try:
            if len(frames) < 2:
                return {'score': 0.0, 'confidence': 0.0, 'inconsistencies_found': False}
            
            # Extract features from frames (simplified - use actual feature extractor)
            frame_features = []
            for frame in frames:
                # Resize and normalize
                resized = cv2.resize(frame, (224, 224))
                normalized = resized.astype(np.float32) / 255.0
                
                # Flatten as simple feature (replace with proper feature extraction)
                features = normalized.flatten()[:2048]  # Truncate to 2048 dims
                frame_features.append(features)
            
            # Convert to tensor
            features_tensor = torch.tensor(np.array(frame_features), dtype=torch.float32).unsqueeze(0)
            features_tensor = features_tensor.to(self.device)
            
            # Run temporal model
            with torch.no_grad():
                temporal_model.to(self.device)
                temporal_model.eval()
                prediction = temporal_model(features_tensor)
                score = prediction.cpu().numpy()[0][0]
            
            # Calculate frame-to-frame differences
            frame_diffs = []
            for i in range(len(frames) - 1):
                diff = np.mean(np.abs(frames[i].astype(float) - frames[i+1].astype(float)))
                frame_diffs.append(diff)
            
            # High variance in frame differences suggests inconsistencies
            diff_variance = np.var(frame_diffs) if frame_diffs else 0
            
            # Additional temporal checks
            optical_flow_score = await self._analyze_optical_flow(frames)
            
            # Combined temporal score
            combined_score = (float(score) * 0.5 + 
                            min(diff_variance / 1000.0, 1.0) * 0.3 + 
                            optical_flow_score * 0.2)
            
            return {
                'score': float(combined_score),
                'confidence': 0.8 if len(frames) > 10 else 0.6,
                'inconsistencies_found': combined_score > 0.6,
                'model_score': float(score),
                'frame_diff_variance': float(diff_variance),
                'optical_flow_score': optical_flow_score,
                'frames_analyzed': len(frames)
            }
            
        except Exception as e:
            logger.error(f"Error detecting temporal inconsistencies: {str(e)}")
            return {'score': 0.0, 'confidence': 0.0, 'inconsistencies_found': False}
    
    async def check_audio_visual_sync(self, video_path: str) -> Dict:
        """
        Check audio-visual synchronization
        Deepfakes often have poor lip-sync or audio mismatch
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with sync analysis results
        """
        try:
            # Check if video has audio
            cap = cv2.VideoCapture(video_path)
            has_audio = self._check_audio_stream(video_path)
            cap.release()
            
            if not has_audio:
                return {
                    'score': 0.0,
                    'confidence': 0.0,
                    'sync_issue': False,
                    'reason': 'no_audio'
                }
            
            # Simplified sync check - in production, use proper lip-sync detection
            # This would involve:
            # 1. Extract audio timestamps and speech segments
            # 2. Detect mouth movements in video frames
            # 3. Compare timing of audio speech with mouth movements
            
            # Placeholder implementation
            sync_score = 0.3  # Assume moderate sync (replace with actual detection)
            
            return {
                'score': sync_score,
                'confidence': 0.7,
                'sync_issue': sync_score > 0.6,
                'has_audio': has_audio
            }
            
        except Exception as e:
            logger.error(f"Error checking audio-visual sync: {str(e)}")
            return {'score': 0.0, 'confidence': 0.0, 'sync_issue': False}
    
    async def detect_motion_artifacts(self, frames: List[np.ndarray]) -> Dict:
        """
        Detect motion artifacts that are common in deepfakes
        
        Args:
            frames: List of video frames
            
        Returns:
            Dictionary with motion artifact analysis
        """
        try:
            if len(frames) < 2:
                return {'score': 0.0, 'artifacts_found': False}
            
            artifacts_scores = []
            
            for i in range(len(frames) - 1):
                # Convert to grayscale
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
                gray2 = cv2.cvtColor(frames[i+1], cv2.COLOR_RGB2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowFarneback(
                    gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0
                )
                
                # Analyze flow magnitude
                magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                
                # Detect unnatural motion patterns
                # High magnitude variance suggests artifacts
                mag_variance = np.var(magnitude)
                artifacts_scores.append(mag_variance)
                
                # Check for discontinuities in motion
                flow_diff = np.abs(np.diff(magnitude, axis=0))
                discontinuity_score = np.mean(flow_diff)
                artifacts_scores.append(discontinuity_score)
            
            avg_artifact_score = np.mean(artifacts_scores) if artifacts_scores else 0
            
            # Normalize score
            normalized_score = min(avg_artifact_score / 100.0, 1.0)
            
            return {
                'score': float(normalized_score),
                'artifacts_found': normalized_score > 0.5,
                'artifact_scores': [float(s) for s in artifacts_scores],
                'frames_analyzed': len(frames) - 1
            }
            
        except Exception as e:
            logger.error(f"Error detecting motion artifacts: {str(e)}")
            return {'score': 0.0, 'artifacts_found': False}
    
    async def _analyze_optical_flow(self, frames: List[np.ndarray]) -> float:
        """Analyze optical flow consistency"""
        if len(frames) < 3:
            return 0.0
        
        try:
            flow_magnitudes = []
            
            for i in range(min(10, len(frames) - 1)):  # Sample first 10 frame pairs
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
                gray2 = cv2.cvtColor(frames[i+1], cv2.COLOR_RGB2GRAY)
                
                flow = cv2.calcOpticalFlowFarneback(
                    gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0
                )
                
                magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                flow_magnitudes.append(np.mean(magnitude))
            
            # Check consistency of flow magnitudes
            if len(flow_magnitudes) > 1:
                variance = np.var(flow_magnitudes)
                # High variance suggests inconsistent motion
                return min(variance / 10.0, 1.0)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error analyzing optical flow: {str(e)}")
            return 0.0
    
    def _check_audio_stream(self, video_path: str) -> bool:
        """Check if video has audio stream"""
        try:
            # Use ffprobe to check for audio stream
            cmd = [
                'ffprobe', '-v', 'error', '-select_streams', 'a:0',
                '-show_entries', 'stream=codec_type', '-of', 'default=nw=1',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return 'audio' in result.stdout.lower()
            
        except Exception as e:
            logger.warning(f"Could not check audio stream: {str(e)}")
            # Fallback: assume video might have audio
            return True
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get video metadata and properties"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            info = {
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'duration_seconds': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
            }
            
            cap.release()
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {}
