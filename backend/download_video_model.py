import os
from huggingface_hub import snapshot_download

# Target directory for video models
CACHE_DIR = "./hf_video_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

VIDEO_MODEL_ID = "tayyabimam/Deepfake"

print(f"Downloading video deepfake model: {VIDEO_MODEL_ID}")
snapshot_download(
    repo_id=VIDEO_MODEL_ID,
    cache_dir=CACHE_DIR,
    local_dir=CACHE_DIR,
    local_dir_use_symlinks=False
)
print(f"✅ Video model downloaded to {CACHE_DIR}")
