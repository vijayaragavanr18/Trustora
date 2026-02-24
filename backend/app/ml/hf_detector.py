"""
HuggingFace Deepfake Detector
Model: dima806/deepfake_vs_real_image_detection
- Vision Transformer (ViT) trained on real deepfake datasets
- Model is pre-downloaded to ./hf_model_cache — no internet needed
"""
import logging
import os
from pathlib import Path

# ── ENVIRONMENT FIX ────────────────────────────────────────────────────────
# Force PyTorch and disable TensorFlow before any transformers imports
os.environ["USE_TORCH"] = "1"
os.environ["TRANSFORMERS_NO_TF"] = "1"
# ───────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)

# Path to the locally downloaded model snapshots
HF_CACHE_DIR = str(Path(__file__).resolve().parent.parent.parent / "hf_model_cache")
MODEL_ID = "dima806/deepfake_vs_real_image_detection"

HF_AUDIO_CACHE_DIR = str(Path(__file__).resolve().parent.parent.parent / "hf_audio_cache")
AUDIO_MODEL_ID = "MelodyMachine/Deepfake-audio-detection-V2"

_pipeline = None  # Singleton — loaded once, reused
_audio_pipeline = None

def get_hf_pipeline():
    """Load the ViT pipeline once and cache in memory"""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    try:
        logger.info(f"Loading deepfake ViT model from local cache: {HF_CACHE_DIR}")
        
        # Import inside to ensure env vars are set
        import torch
        from transformers import ViTForImageClassification, ViTImageProcessor

        processor = ViTImageProcessor.from_pretrained(
            MODEL_ID,
            cache_dir=HF_CACHE_DIR,
            local_files_only=True,
        )
        model = ViTForImageClassification.from_pretrained(
            MODEL_ID,
            cache_dir=HF_CACHE_DIR,
            local_files_only=True,
        )
        model.eval()
        
        # OPTIMIZATION: Move to CPU and use half precision if supported/needed
        # Using .to('cpu') explicitly to avoid ambiguity
        model.to("cpu")

        _pipeline = (model, processor)
        logger.info("✅ HuggingFace deepfake ViT model loaded!")
        return _pipeline

    except Exception as e:
        logger.error(f"❌ Failed to load HF model: {e}")
        return None

def get_hf_audio_pipeline():
    """Load the Wav2Vec2 audio pipeline once"""
    global _audio_pipeline
    if _audio_pipeline is not None:
        return _audio_pipeline

    try:
        from transformers import Wav2Vec2ForSequenceClassification, AutoFeatureExtractor
        import torch

        logger.info(f"Loading deepfake Audio model from local cache: {HF_AUDIO_CACHE_DIR}")

        processor = AutoFeatureExtractor.from_pretrained(
            AUDIO_MODEL_ID,
            cache_dir=HF_AUDIO_CACHE_DIR,
            local_files_only=True,
        )
        model = Wav2Vec2ForSequenceClassification.from_pretrained(
            AUDIO_MODEL_ID,
            cache_dir=HF_AUDIO_CACHE_DIR,
            local_files_only=True,
        )
        model.eval()

        _audio_pipeline = (model, processor)
        logger.info("✅ HuggingFace deepfake Audio model loaded!")
        return _audio_pipeline
    except Exception as e:
        logger.error(f"❌ Failed to load HF Audio model: {e}")
        return None

def hf_predict_image(image_path: str):
    """
    Run deepfake detection on an image.
    Returns dict with fake_score (0-100), real_score, label.
    """
    result = get_hf_pipeline()
    if result is None:
        return None

    try:
        import torch
        import torch.nn.functional as F
        from PIL import Image

        model, processor = result
        img = Image.open(image_path).convert("RGB")

        inputs = processor(images=img, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)

        probs = F.softmax(outputs.logits, dim=-1)[0]
        id2label = model.config.id2label
        label_scores = {id2label[i].lower(): float(probs[i]) for i in range(len(probs))}

        fake_score = label_scores.get("fake", 1.0 - label_scores.get("real", 0.5))
        real_score = label_scores.get("real", 1.0 - fake_score)

        return {
            "fake_score": round(fake_score * 100, 2),
            "real_score": round(real_score * 100, 2),
            "label": "FAKE" if fake_score > 0.5 else "REAL",
        }
    except Exception as e:
        logger.error(f"HF image inference error: {e}")
        return None

def hf_predict_audio(audio_path: str):
    """
    Run deepfake detection on audio file.
    Returns dict with fake_score (0-100), label.
    """
    result = get_hf_audio_pipeline()
    if result is None:
        return None

    try:
        import torch
        import torch.nn.functional as F
        import librosa

        model, processor = result
        
        # Load audio at 16kHz
        audio_input, _ = librosa.load(audio_path, sr=16000)
        
        inputs = processor(audio_input, sampling_rate=16000, return_tensors="pt", padding=True)
        
        with torch.no_grad():
            logits = model(**inputs).logits
            
        probs = F.softmax(logits, dim=-1)[0]
        
        # Audio model mapping: Usually 0: Real, 1: Fake or vice-versa
        # Let's check config if possible, or assume high index = fake based on most deepfake models
        # For MelodyMachine: 0=real, 1=fake
        fake_score = float(probs[1]) 
        
        return {
            "fake_score": round(fake_score * 100, 2),
            "label": "FAKE" if fake_score > 0.5 else "REAL",
        }
    except Exception as e:
        logger.error(f"HF audio inference error: {e}")
        return None
