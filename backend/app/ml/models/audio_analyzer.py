"""
Audio Analysis Pipeline
Spectral analysis, voice synthesis detection, audio compression artifacts
"""
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Analyzes audio for synthesis and manipulation artifacts"""
    
    def __init__(self):
        self.sample_rate = 16000
        self.n_mels = 128
        self.n_fft = 2048
        self.hop_length = 512
    
    async def spectral_analysis(self, audio_path: str) -> Dict:
        """
        Perform spectral analysis to detect anomalies
        Synthetic voices often have spectral artifacts
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with spectral analysis results
        """
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Compute mel spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio, 
                sr=sr, 
                n_mels=self.n_mels,
                n_fft=self.n_fft,
                hop_length=self.hop_length
            )
            
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Analyze spectral characteristics
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
            
            # Check for unnatural patterns
            # Synthetic voices often have:
            # 1. Unnaturally smooth spectral contours
            # 2. Missing high-frequency components
            # 3. Regular periodic patterns
            
            # Calculate smoothness (variance of spectral centroid)
            centroid_variance = np.var(spectral_centroid)
            smoothness_score = 1.0 - min(centroid_variance / 1000000.0, 1.0)
            
            # Check high frequency content
            high_freq_energy = np.mean(mel_spec_db[-20:, :])  # Top 20 mel bands
            low_freq_energy = np.mean(mel_spec_db[:20, :])    # Bottom 20 mel bands
            
            freq_ratio = abs(high_freq_energy / low_freq_energy) if low_freq_energy != 0 else 0
            
            # Natural speech typically has more high frequency content
            freq_score = 1.0 - min(freq_ratio, 1.0)
            
            # Check for periodic artifacts
            autocorr = np.correlate(audio, audio, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            periodicity_score = np.max(autocorr[100:500]) / np.max(autocorr) if len(autocorr) > 500 else 0
            
            # Combined spectral score
            spectral_score = (smoothness_score * 0.4 + 
                            freq_score * 0.4 + 
                            periodicity_score * 0.2)
            
            return {
                'score': float(spectral_score),
                'smoothness_score': float(smoothness_score),
                'frequency_ratio_score': float(freq_score),
                'periodicity_score': float(periodicity_score),
                'spectral_features': {
                    'centroid_mean': float(np.mean(spectral_centroid)),
                    'centroid_var': float(centroid_variance),
                    'rolloff_mean': float(np.mean(spectral_rolloff)),
                    'bandwidth_mean': float(np.mean(spectral_bandwidth))
                }
            }
            
        except Exception as e:
            logger.error(f"Error in spectral analysis: {str(e)}")
            return {'score': 0.0}
    
    async def detect_voice_synthesis(self, audio_path: str) -> Dict:
        """
        Detect voice synthesis using multiple techniques
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with synthesis detection results
        """
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Extract MFCC features (commonly used for voice synthesis detection)
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            
            # Statistical analysis of MFCC
            mfcc_mean = np.mean(mfcc, axis=1)
            mfcc_var = np.var(mfcc, axis=1)
            mfcc_delta = librosa.feature.delta(mfcc)
            
            # Check for unnatural patterns in MFCCs
            # Real speech has more variation in MFCC coefficients
            coefficient_variation = np.mean(mfcc_var)
            
            # Low variation suggests synthesis
            synthesis_score_1 = 1.0 - min(coefficient_variation / 100.0, 1.0)
            
            # Analyze formant frequencies
            # Synthetic voices often have irregular formants
            formant_score = await self._analyze_formants(audio, sr)
            
            # Check for phase discontinuities
            phase_score = self._detect_phase_discontinuities(audio)
            
            # Analyze pitch naturalness
            pitch_score = await self._analyze_pitch_naturalness(audio, sr)
            
            # Combined synthesis detection score
            synthesis_score = (synthesis_score_1 * 0.3 + 
                             formant_score * 0.3 + 
                             phase_score * 0.2 + 
                             pitch_score * 0.2)
            
            # Calculate confidence based on audio length
            duration = len(audio) / sr
            confidence = min(duration / 5.0, 1.0)  # More confident with longer audio
            
            return {
                'score': float(synthesis_score),
                'confidence': float(confidence),
                'is_synthetic': synthesis_score > 0.6,
                'mfcc_score': float(synthesis_score_1),
                'formant_score': float(formant_score),
                'phase_score': float(phase_score),
                'pitch_score': float(pitch_score),
                'audio_duration': float(duration)
            }
            
        except Exception as e:
            logger.error(f"Error detecting voice synthesis: {str(e)}")
            return {'score': 0.0, 'confidence': 0.0, 'is_synthetic': False}
    
    async def detect_compression_artifacts(self, audio_path: str) -> Dict:
        """
        Detect audio compression artifacts
        Multiple compressions or unusual compression can indicate manipulation
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with compression artifact analysis
        """
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=None)  # Keep original sample rate
            
            # Analyze frequency spectrum for compression artifacts
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            
            # Look for spectral holes (common in heavy compression)
            # Calculate spectral flatness
            spectral_flatness = librosa.feature.spectral_flatness(y=audio)[0]
            flatness_score = np.mean(spectral_flatness)
            
            # High flatness suggests over-compression
            compression_score = min(flatness_score * 2.0, 1.0)
            
            # Check for quantization noise
            # Calculate signal-to-noise ratio estimate
            noise_floor = np.percentile(magnitude, 10)
            signal_level = np.percentile(magnitude, 90)
            snr_estimate = signal_level / noise_floor if noise_floor > 0 else 100
            
            # Low SNR suggests heavy compression
            snr_score = 1.0 - min(snr_estimate / 100.0, 1.0)
            
            # Check for aliasing artifacts
            nyquist = sr / 2
            high_freq_artifacts = np.mean(magnitude[int(len(magnitude) * 0.9):])
            aliasing_score = min(high_freq_artifacts / np.max(magnitude), 1.0)
            
            # Combined compression artifact score
            artifact_score = (compression_score * 0.4 + 
                            snr_score * 0.4 + 
                            aliasing_score * 0.2)
            
            return {
                'score': float(artifact_score),
                'artifacts_detected': artifact_score > 0.6,
                'spectral_flatness': float(flatness_score),
                'snr_estimate': float(snr_estimate),
                'aliasing_score': float(aliasing_score),
                'sample_rate': int(sr)
            }
            
        except Exception as e:
            logger.error(f"Error detecting compression artifacts: {str(e)}")
            return {'score': 0.0, 'artifacts_detected': False}
    
    async def _analyze_formants(self, audio: np.ndarray, sr: int) -> float:
        """Analyze formant frequencies for naturalness"""
        try:
            # Simplified formant analysis
            # In production, use proper formant extraction (e.g., LPC analysis)
            
            # Apply pre-emphasis filter
            emphasized = librosa.effects.preemphasis(audio)
            
            # Compute LPC coefficients
            # This is a simplified approach
            windowed = emphasized[:min(len(emphasized), sr)]  # First second
            
            if len(windowed) < 100:
                return 0.0
            
            # Calculate spectral peaks (rough formant approximation)
            fft = np.fft.rfft(windowed)
            magnitude = np.abs(fft)
            
            # Find peaks
            peaks, _ = signal.find_peaks(magnitude, height=np.max(magnitude) * 0.1)
            
            # Natural speech typically has 3-5 formants in the analysis range
            formant_count = len(peaks)
            
            if formant_count < 2 or formant_count > 8:
                return 0.7  # Suspicious formant structure
            
            return 0.3  # Reasonable formant structure
            
        except Exception as e:
            logger.error(f"Error analyzing formants: {str(e)}")
            return 0.0
    
    def _detect_phase_discontinuities(self, audio: np.ndarray) -> float:
        """Detect phase discontinuities that suggest splicing or synthesis"""
        try:
            # Compute instantaneous phase
            analytic_signal = signal.hilbert(audio)
            instantaneous_phase = np.unwrap(np.angle(analytic_signal))
            
            # Calculate phase derivative
            phase_derivative = np.diff(instantaneous_phase)
            
            # Look for sudden jumps in phase
            phase_jumps = np.abs(phase_derivative) > np.std(phase_derivative) * 3
            jump_rate = np.sum(phase_jumps) / len(phase_jumps)
            
            # High jump rate suggests discontinuities
            return min(jump_rate * 10.0, 1.0)
            
        except Exception as e:
            logger.error(f"Error detecting phase discontinuities: {str(e)}")
            return 0.0
    
    async def _analyze_pitch_naturalness(self, audio: np.ndarray, sr: int) -> float:
        """Analyze pitch contour for naturalness"""
        try:
            # Extract pitch using librosa
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
            
            # Get pitch contour
            pitch_contour = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_contour.append(pitch)
            
            if len(pitch_contour) < 10:
                return 0.0
            
            # Analyze pitch variation
            pitch_variance = np.var(pitch_contour)
            pitch_range = np.max(pitch_contour) - np.min(pitch_contour)
            
            # Very low variance or very high variance is suspicious
            if pitch_variance < 100 or pitch_variance > 10000:
                return 0.7
            
            # Check for unnatural jumps
            pitch_diff = np.abs(np.diff(pitch_contour))
            large_jumps = np.sum(pitch_diff > 50) / len(pitch_diff)
            
            if large_jumps > 0.3:
                return 0.6
            
            return 0.2  # Natural pitch characteristics
            
        except Exception as e:
            logger.error(f"Error analyzing pitch: {str(e)}")
            return 0.0
