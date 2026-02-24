
import asyncio
import os
import numpy as np
from PIL import Image
import sys

# Add app to path
sys.path.append(os.getcwd())

from app.ml.deepfake_detector import DeepfakeDetector

async def test_detector():
    print("Initializing detector...")
    detector = DeepfakeDetector()
    
    print("Creating dummy image...")
    # Create a black image
    img = Image.fromarray(np.zeros((300, 300, 3), dtype=np.uint8))
    img.save("test_image.jpg")
    
    try:
        print("Analyzing image...")
        result = await detector.analyze_image("test_image.jpg")
        print("Analysis complete!")
        print(f"Score: {result['score']}")
        print(f"Risk: {result['risk_level']}")
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists("test_image.jpg"):
            os.remove("test_image.jpg")

if __name__ == "__main__":
    asyncio.run(test_detector())
