# 🚀 Quick Start Guide

Get started with the Deepfake Detection & Trusted Capture System in minutes!

## Step 1: Setup (2 minutes)

```bash
# Run the setup script
python setup.py
```

This will:
- ✅ Check Python version
- ✅ Install all dependencies
- ✅ Create necessary directories
- ✅ Create .env configuration file

## Step 2: Configure (2 minutes)

Edit the `.env` file with your settings:

```bash
# Minimal configuration for testing
BLOCKCHAIN_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
API_PORT=8000
DEEPFAKE_THRESHOLD=0.7
```

**For blockchain features:**
1. Sign up at [Infura.io](https://infura.io)
2. Get your API key
3. Update `BLOCKCHAIN_PROVIDER_URL` in `.env`

## Step 3: Start the API (1 minute)

```bash
python api.py
```

The API will start at: **http://localhost:8000**

## Step 4: Test It! (1 minute)

### Option A: Use the Interactive Docs

Open in your browser: **http://localhost:8000/docs**

Click on any endpoint → "Try it out" → Upload a file → Execute

### Option B: Use cURL

```bash
# Test image analysis
curl -X POST "http://localhost:8000/api/analyze/image" \
  -F "file=@your_image.jpg"

# Test health check
curl "http://localhost:8000/health"
```

### Option C: Use Python

```python
import asyncio
from deepfake_detector import get_detector

async def quick_test():
    detector = get_detector()
    await detector.load_models()
    result = await detector.analyze_image('your_image.jpg')
    print(f"Score: {result['score']}")
    print(f"Is Deepfake: {result['is_deepfake']}")

asyncio.run(quick_test())
```

## What's Next?

### Download Pre-trained Models (Recommended)

For better accuracy, download pre-trained weights:

1. **XceptionNet**: [FaceForensics](https://github.com/ondyari/FaceForensics)
2. **EfficientNet**: [DFDC Challenge](https://github.com/selimsef/dfdc_deepfake_challenge)
3. **Temporal Model**: [Video Detection](https://github.com/cuijianzhu/Video-Deepfake-Detection)

Place weights in: `models/weights/`

### Enable Blockchain Features

1. Get test ETH from [Sepolia Faucet](https://sepoliafaucet.com)
2. Deploy the smart contract (`contracts/TrustedCapture.sol`)
3. Update `CONTRACT_ADDRESS` in `.env`
4. Add your wallet `PRIVATE_KEY` to `.env`

### Try More Features

```bash
# Analyze video
curl -X POST "http://localhost:8000/api/analyze/video" \
  -F "file=@your_video.mp4"

# Analyze audio
curl -X POST "http://localhost:8000/api/analyze/audio" \
  -F "file=@your_audio.mp3"

# Create trusted capture
curl -X POST "http://localhost:8000/api/trusted-capture/create" \
  -F "file=@original.jpg" \
  -F "user_id=user123"
```

## Common Issues

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "Models not loading"
- System will use base models if weights not found
- Download pre-trained weights for better accuracy
- Check `models/weights/` directory

### "Blockchain not connected"
- Verify `BLOCKCHAIN_PROVIDER_URL` in `.env`
- Check internet connection
- System works without blockchain for detection only

## Need Help?

1. Check the full [README.md](README.md)
2. View API documentation at `/docs`
3. Run examples: `python examples.py`
4. Check logs for detailed error messages

---

**You're ready to detect deepfakes! 🎉**

The system works out of the box with base models. For production use, consider downloading pre-trained weights and configuring blockchain features.
