"""
Configuration settings for Deepfake Detection System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# ML Model Configuration
class ModelConfig:
    XCEPTION_MODEL_PATH = os.getenv('XCEPTION_MODEL_PATH', './models/weights/xception_weights.h5')
    EFFICIENTNET_MODEL_PATH = os.getenv('EFFICIENTNET_MODEL_PATH', './models/weights/efficientnet_weights.h5')
    TEMPORAL_TRANSFORMER_PATH = os.getenv('TEMPORAL_TRANSFORMER_PATH', './models/weights/temporal_transformer.pth')
    
    # Image processing
    IMAGE_SIZE = (299, 299)
    BATCH_SIZE = 32
    
    # Video processing
    FRAMES_PER_SECOND = 1  # Reduce FPS for faster processing
    MAX_FRAMES = 30       # Cap at 30 frames total (enough for detection)
    
    # Audio processing
    SAMPLE_RATE = 16000
    N_MELS = 128
    
    # Ensemble weights
    XCEPTION_WEIGHT = 0.3
    EFFICIENTNET_WEIGHT = 0.3
    TEMPORAL_WEIGHT = 0.2
    AUDIO_WEIGHT = 0.1
    METADATA_WEIGHT = 0.1

# Blockchain Configuration
class BlockchainConfig:
    PROVIDER_URL = os.getenv('BLOCKCHAIN_PROVIDER_URL', 'https://sepolia.infura.io/v3/YOUR_KEY')
    NETWORK = os.getenv('BLOCKCHAIN_NETWORK', 'sepolia')
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')
    PRIVATE_KEY = os.getenv('PRIVATE_KEY', '')
    GAS_LIMIT = 500000
    
    # Smart contract ABI (simplified version)
    CONTRACT_ABI = [
        {
            "inputs": [
                {"internalType": "bytes32", "name": "fileHash", "type": "bytes32"},
                {"internalType": "bytes", "name": "metadata", "type": "bytes"}
            ],
            "name": "createTimestamp",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "bytes32", "name": "fileHash", "type": "bytes32"}],
            "name": "verifyTimestamp",
            "outputs": [
                {"internalType": "bool", "name": "", "type": "bool"},
                {"internalType": "uint256", "name": "", "type": "uint256"},
                {"internalType": "bytes", "name": "", "type": "bytes"}
            ],
            "stateMutability": "view",
            "type": "function"
        }
    ]

# API Configuration
class APIConfig:
    HOST = os.getenv('API_HOST', '0.0.0.0')
    PORT = int(os.getenv('API_PORT', 8000))
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 100))
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    TEMP_UPLOAD_DIR = Path(os.getenv('TEMP_UPLOAD_DIR', './temp_uploads'))
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.ogg'}

# Security Configuration
class SecurityConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'your-encryption-key-change-in-production')

# Analysis Thresholds
class AnalysisConfig:
    DEEPFAKE_THRESHOLD = float(os.getenv('DEEPFAKE_THRESHOLD', 0.7))
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.6))
    
    # Risk classification
    RISK_LOW = 0.3
    RISK_MEDIUM = 0.6
    RISK_HIGH = 0.8

# Database Configuration
class DatabaseConfig:
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./deepfake_db.sqlite')
