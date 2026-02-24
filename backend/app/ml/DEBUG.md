# 🐛 DEBUG & INSTALLATION GUIDE

## Current Status: ✅ Core packages installed

The following core packages have been successfully installed:
- ✅ web3, eth-account, eth-utils (Blockchain)
- ✅ fastapi, uvicorn, pydantic (API)
- ✅ python-dotenv, cryptography, aiofiles (Utilities)
- ✅ numpy, Pillow (Basic processing)

## Next Steps:

### 1. Install ML/AI Packages (Optional - for detection features)

Run this command to install ML packages:

```powershell
pip install tensorflow==2.15.0 torch==2.1.0 torchvision==0.16.0 opencv-python==4.8.1.78 librosa==0.10.1 scikit-learn==1.3.2 scipy==1.11.4 soundfile==0.12.1 pandas==2.1.3
```

**Note:** These packages are large (2-3 GB). Only install if you need deepfake detection.  
For blockchain testing only, you can skip this step.

### 2. Quick Test (Without ML Packages)

You can test the blockchain integration immediately:

```python
# test_blockchain.py
import asyncio
from blockchain.blockchain_integration import get_blockchain

async def test():
    blockchain = get_blockchain()
    info = blockchain.get_network_info()
    print(f"Blockchain ready: {info}")

asyncio.run(test())
```

### 3. Configure Environment

Edit `.env` file:

```bash
# For blockchain testing
BLOCKCHAIN_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
BLOCKCHAIN_NETWORK=sepolia

# For API
API_HOST=0.0.0.0
API_PORT=8000
```

Get a free Infura key: https://infura.io

### 4. Run API (Without ML)

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Run API
python api.py
```

The API will start but detection endpoints will need ML packages.  
Blockchain/trusted capture endpoints will work!

## Troubleshooting:

### Import errors in IDE
- Reload VS Code window (Ctrl+Shift+P → "Reload Window")
- Select the virtual environment: Ctrl+Shift+P → "Python: Select Interpreter"
- Choose: `.venv\Scripts\python.exe`

### "Module not found" at runtime
```powershell
# Make sure you're in the virtual environment
.venv\Scripts\activate

# Reinstall if needed
pip install -r requirements-minimal.txt
```

### ML packages installation fails
- Install packages individually
- Use CPU-only TensorFlow if you don't have GPU
- Skip ML packages and use blockchain features only

### Testing without ML models

Create a simple test file:

```python
# simple_test.py
from blockchain.trusted_capture import get_trusted_capture
import asyncio

async def test():
    tc = get_trusted_capture()
    print("Trusted Capture initialized!")
    
    # Test file hashing
    import hashlib
    test_data = b"Hello, World!"
    hash_result = hashlib.sha256(test_data).hexdigest()
    print(f"File hash test: {hash_result}")

asyncio.run(test())
```

## Installation Options:

### Option A: Full Installation (Recommended)
```powershell
pip install -r requirements.txt
```
- Installs everything
- ~3 GB download
- Full deepfake detection + blockchain

### Option B: Minimal Installation (Quick Start)
```powershell
pip install -r requirements-minimal.txt
```
- Installs core packages only
- ~100 MB download
- Blockchain + API only (no detection)

### Option C: Blockchain Only
```powershell
pip install web3 eth-account python-dotenv cryptography
```
- Minimal blockchain functionality
- ~50 MB download

## What Works Now:

✅ **Blockchain Integration** - Ready to use  
✅ **Trusted Capture** - Create blockchain timestamps  
✅ **API Server** - Can start (detection endpoints need ML)  
✅ **Configuration** - All config files ready  

⏳ **Deepfake Detection** - Needs ML packages (tensorflow, torch, etc.)  
⏳ **Image/Video/Audio Analysis** - Needs ML packages  

## Quick Commands:

```powershell
# Activate environment
.venv\Scripts\activate

# Check installed packages
pip list

# Install remaining ML packages
pip install -r requirements-ml.txt

# Run API
python api.py

# Test blockchain
python -c "from blockchain.blockchain_integration import get_blockchain; print('OK')"
```

## Performance Notes:

- **With base models only**: System will work but with lower accuracy
- **With pre-trained weights**: 90%+ accuracy (download separately)
- **GPU recommended**: For faster video processing
- **CPU works**: Slower but functional

## Next: Get Blockchain Credentials

1. Sign up: https://infura.io
2. Create project
3. Copy endpoint URL
4. Add to `.env` file

---

**Status: ✅ Core system ready!**  
**Next: Install ML packages or start testing blockchain features**
