"""
Model Loader - Responsible for loading pre-trained models
"""
import os
import asyncio
import logging
from pathlib import Path
import tensorflow as tf
import torch
try:
    from app.ml.config import ModelConfig
except ImportError:
    try:
        from ..config import ModelConfig
    except ImportError:
        from config import ModelConfig

logger = logging.getLogger(__name__)


class ModelLoader:
    """Load and manage pre-trained deepfake detection models"""
    
    def __init__(self):
        self.config = ModelConfig()
        self._ensure_model_directories()
    
    def _ensure_model_directories(self):
        """Create necessary directories for model weights"""
        weights_dir = Path('./models/weights')
        weights_dir.mkdir(parents=True, exist_ok=True)
    
    async def load_xception(self):
        """Deprecated: Use load_xception_sync directly"""
        return self.load_xception_sync()

    def load_xception_sync(self):
        """
        Load Xception model for deepfake detection
        Pre-trained on FaceForensics++ dataset
        """
        print("DEBUG: Entering load_xception_sync")
        from tensorflow.keras.models import load_model
        print("DEBUG: Imported load_model")
        try:
            model_path = Path(self.config.XCEPTION_MODEL_PATH)
            print(f"DEBUG: Model path is {model_path}")
            
            if model_path.exists():
                logger.info(f"Loading Xception model from {model_path}")
                print(f"DEBUG: Loading model from disk...")
                model = load_model(str(model_path))
                print(f"DEBUG: Model loaded from disk")
            else:
                logger.warning(f"Xception weights not found at {model_path}. Building base model...")
                print(f"DEBUG: Weights not found, building base model...")
                model = self._build_xception_model()
                print(f"DEBUG: Base model built")
                logger.info("Note: Using base Xception. Download pre-trained weights for better performance.")
            
            return model
            
        except Exception as e:
            logger.error(f"Error loading Xception model: {str(e)}")
            print(f"DEBUG: Error loading Xception: {e}")
            import traceback
            traceback.print_exc()
            return self._build_xception_model()
    
    async def load_efficientnet(self):
        """Deprecated: Use load_efficientnet_sync directly"""
        return self.load_efficientnet_sync()

    def load_efficientnet_sync(self):
        """
        Load EfficientNet model for deepfake detection
        """
        print("DEBUG: Entering load_efficientnet_sync")
        from tensorflow.keras.models import load_model
        try:
            model_path = Path(self.config.EFFICIENTNET_MODEL_PATH)
            
            if model_path.exists():
                logger.info(f"Loading EfficientNet model from {model_path}")
                model = load_model(str(model_path))
            else:
                logger.warning(f"EfficientNet weights not found at {model_path}. Building base model...")
                print(f"DEBUG: Building EfficientNet base model...")
                model = self._build_efficientnet_model()
                print(f"DEBUG: EfficientNet base model built")
                logger.info("Note: Using base EfficientNet. Download pre-trained weights for better performance.")
            
            return model
            
        except Exception as e:
            logger.error(f"Error loading EfficientNet model: {str(e)}")
            print(f"DEBUG: Error loading EfficientNet: {e}")
            return self._build_efficientnet_model()
    
    async def load_temporal_model(self):
        """
        Load Temporal Transformer model for video analysis
        """
        try:
            model_path = Path(self.config.TEMPORAL_TRANSFORMER_PATH)
            
            if model_path.exists():
                logger.info(f"Loading Temporal Transformer from {model_path}")
                model = torch.load(str(model_path))
                model.eval()
            else:
                logger.warning(f"Temporal model not found at {model_path}. Building base model...")
                model = self._build_temporal_model()
                logger.info("Note: Using base temporal model. Download pre-trained weights for better performance.")
            
            return model
            
        except Exception as e:
            logger.error(f"Error loading temporal model: {str(e)}")
            return self._build_temporal_model()
    
    def _build_xception_model(self):
        """Build Xception model architecture"""
        # Explicit import to avoid attribute errors
        from tensorflow.keras.applications import Xception
        from tensorflow.keras.layers import Dense, Dropout
        from tensorflow.keras.models import Model
        from tensorflow.keras.optimizers import Adam
        
        base_model = Xception(
            include_top=False,
            weights='imagenet',
            input_shape=(299, 299, 3),
            pooling='avg'
        )
        
        # Add classification head
        x = base_model.output
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.5)(x)
        output = Dense(1, activation='sigmoid', name='deepfake_output')(x)
        
        model = Model(inputs=base_model.input, outputs=output)
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=0.0001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info("Built Xception model architecture")
        return model
    
    def _build_efficientnet_model(self):
        """Build EfficientNet model architecture"""
        # Explicit import for stability
        from tensorflow.keras.applications import EfficientNetB4
        from tensorflow.keras.layers import Dense, Dropout
        from tensorflow.keras.models import Model
        from tensorflow.keras.optimizers import Adam
        
        base_model = EfficientNetB4(
            include_top=False,
            weights='imagenet',
            input_shape=(299, 299, 3),
            pooling='avg'
        )
        
        # Add classification head
        x = base_model.output
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.5)(x)
        output = Dense(1, activation='sigmoid', name='deepfake_output')(x)
        
        model = Model(inputs=base_model.input, outputs=output)
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=0.0001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info("Built EfficientNet model architecture")
        return model
    
    def _build_temporal_model(self):
        """Build simple temporal model (placeholder for actual transformer)"""
        import torch.nn as nn
        
        class SimpleTemporalModel(nn.Module):
            def __init__(self):
                super(SimpleTemporalModel, self).__init__()
                self.lstm = nn.LSTM(2048, 512, num_layers=2, batch_first=True)
                self.fc1 = nn.Linear(512, 256)
                self.dropout = nn.Dropout(0.5)
                self.fc2 = nn.Linear(256, 1)
                self.sigmoid = nn.Sigmoid()
            
            def forward(self, x):
                lstm_out, _ = self.lstm(x)
                out = self.fc1(lstm_out[:, -1, :])
                out = self.dropout(out)
                out = self.fc2(out)
                out = self.sigmoid(out)
                return out
        
        model = SimpleTemporalModel()
        logger.info("Built temporal model architecture")
        return model
    
    @staticmethod
    def download_pretrained_weights():
        """
        Helper function to download pre-trained weights
        Note: Implement actual download logic based on your hosting
        """
        instructions = """
        To download pre-trained weights:
        
        1. Xception Model:
           - Download from: https://github.com/ondyari/FaceForensics/tree/master/classification
           - Place in: ./models/weights/xception_weights.h5
        
        2. EfficientNet Model:
           - Download from: https://github.com/selimsef/dfdc_deepfake_challenge
           - Place in: ./models/weights/efficientnet_weights.h5
        
        3. Temporal Transformer:
           - Download from: https://github.com/cuijianzhu/Video-Deepfake-Detection
           - Place in: ./models/weights/temporal_transformer.pth
        
        Alternatively, train your own models on datasets:
           - FaceForensics++
           - Celeb-DF
           - DFDC (Deepfake Detection Challenge)
        """
        print(instructions)
        return instructions
