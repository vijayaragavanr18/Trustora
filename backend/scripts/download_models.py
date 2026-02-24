import os
import requests
from tqdm import tqdm
from pathlib import Path

# URLs for common deepfake detection weights (FaceForensics++ & EfficientNet)
WEIGHTS = {
    "xception_weights.h5": "https://github.com/ondyari/FaceForensics/releases/download/v1.0/xception_full_resnet.h5",
    "efficientnet_weights.h5": "https://github.com/selimsef/dfdc_deepfake_challenge/releases/download/weights/final_111_nm_0.450.pth" # Placeholder for EfficientNet (PyTorch usually)
}

def download_file(url, target_path):
    print(f"Downloading {url} to {target_path}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(target_path, 'wb') as file, tqdm(
        desc=target_path.name,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

def main():
    # Target directory
    target_dir = Path("./models/weights")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print("--- Trustora Model Downloader ---")
    print("This script will download ~500MB of pre-trained AI weights.")
    
    for filename, url in WEIGHTS.items():
        target_path = target_dir / filename
        if target_path.exists():
            print(f"[SKIP] {filename} already exists.")
            continue
            
        try:
            download_file(url, target_path)
            print(f"[OK] {filename} downloaded successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to download {filename}: {e}")

if __name__ == "__main__":
    # Ensure requests and tqdm are installed
    try:
        import requests, tqdm
    except ImportError:
        print("Installing required libraries: requests, tqdm...")
        os.system("pip install requests tqdm")
        
    main()
