"""
Setup and Installation Script
Helps download model weights and configure the environment
"""
import os
import sys
from pathlib import Path
import subprocess


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        return False
    
    print("✅ Python version is compatible")
    return True


def install_dependencies():
    """Install required dependencies"""
    print_header("Installing Dependencies")
    
    print("Installing Python packages from requirements.txt...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print_header("Creating Directory Structure")
    
    directories = [
        "models/weights",
        "temp_uploads",
        "database",
        "static/heatmaps"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    return True


def create_env_file():
    """Create .env file from example if it doesn't exist"""
    print_header("Configuring Environment")
    
    env_file = Path(".env")
    example_file = Path(".env.example")
    
    if env_file.exists():
        print("ℹ️  .env file already exists")
        return True
    
    if example_file.exists():
        import shutil
        shutil.copy(example_file, env_file)
        print("✅ Created .env file from .env.example")
        print("⚠️  Please edit .env file with your configuration")
        return True
    else:
        print("❌ .env.example file not found")
        return False


def print_model_download_instructions():
    """Print instructions for downloading pre-trained models"""
    print_header("Model Weights Setup")
    
    instructions = """
    To use pre-trained models, you need to download the model weights:
    
    1. XCEPTION MODEL:
       - Download from: https://github.com/ondyari/FaceForensics/tree/master/classification
       - Or train your own on FaceForensics++ dataset
       - Place in: ./models/weights/xception_weights.h5
    
    2. EFFICIENTNET MODEL:
       - Download from: https://github.com/selimsef/dfdc_deepfake_challenge
       - Or use transfer learning on your own dataset
       - Place in: ./models/weights/efficientnet_weights.h5
    
    3. TEMPORAL TRANSFORMER:
       - Download from: https://github.com/cuijianzhu/Video-Deepfake-Detection
       - Or implement your own temporal model
       - Place in: ./models/weights/temporal_transformer.pth
    
    NOTE: The system will work with base models if weights are not found,
    but detection accuracy will be lower. For production use, pre-trained
    weights are highly recommended.
    
    DATASETS FOR TRAINING:
    - FaceForensics++: https://github.com/ondyari/FaceForensics
    - Celeb-DF: https://github.com/yuezunli/celeb-deepfakeforensics
    - DFDC: https://deepfakedetectionchallenge.ai/
    """
    
    print(instructions)


def print_blockchain_setup():
    """Print blockchain setup instructions"""
    print_header("Blockchain Setup")
    
    instructions = """
    BLOCKCHAIN CONFIGURATION:
    
    1. GET INFURA/ALCHEMY API KEY:
       - Sign up at https://infura.io or https://www.alchemy.com
       - Create a new project
       - Copy your API endpoint URL
    
    2. UPDATE .env FILE:
       - BLOCKCHAIN_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_KEY
       - BLOCKCHAIN_NETWORK=sepolia (or your preferred testnet)
    
    3. DEPLOY SMART CONTRACT (Optional):
       - Use the provided Solidity contract in contracts/
       - Deploy to Sepolia testnet using Remix or Hardhat
       - Update CONTRACT_ADDRESS in .env
    
    4. GET TEST ETHER:
       - For Sepolia: https://sepoliafaucet.com
       - For Goerli: https://goerlifaucet.com
    
    5. WALLET SETUP:
       - Generate a wallet address
       - Store private key securely in .env
       - NEVER commit .env to version control
    
    For production, consider using:
    - Private blockchain (Hyperledger Fabric)
    - Layer 2 solutions (Polygon) for lower fees
    - Hardware wallet for key management
    """
    
    print(instructions)


def print_completion_message():
    """Print completion message and next steps"""
    print_header("Setup Complete!")
    
    message = """
    ✅ Setup completed successfully!
    
    NEXT STEPS:
    
    1. Download model weights (see instructions above)
    2. Configure blockchain settings in .env
    3. Test the API:
       python api.py
    
    4. Access the API at: http://localhost:8000
    5. View API documentation at: http://localhost:8000/docs
    
    TESTING:
    - Use test_api.py to run automated tests
    - Upload sample images/videos to test detection
    - Create trusted captures with test files
    
    DOCUMENTATION:
    - See README.md for detailed usage instructions
    - API documentation available at /docs endpoint
    
    SUPPORT:
    - Check logs for any errors
    - Ensure all dependencies are properly installed
    - Verify blockchain connection if using trusted capture
    
    Happy detecting! 🔍
    """
    
    print(message)


def main():
    """Main setup function"""
    print_header("Deepfake Detection System Setup")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Warning: Some dependencies failed to install")
        print("You may need to install them manually")
    
    # Print model download instructions
    print_model_download_instructions()
    
    # Print blockchain setup
    print_blockchain_setup()
    
    # Print completion message
    print_completion_message()


if __name__ == "__main__":
    main()
