import os
from huggingface_hub import snapshot_download

# Target directory for audio models
CACHE_DIR = "./hf_audio_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

AUDIO_MODEL_ID = "MelodyMachine/Deepfake-audio-detection-V2"

print(f"Downloading audio deepfake model: {AUDIO_MODEL_ID}")
snapshot_download(
    repo_id=AUDIO_MODEL_ID,
    cache_dir=CACHE_DIR,
    local_dir=CACHE_DIR,
    local_dir_use_symlinks=False,
    # Ignore large unneeded files if any
    ignore_patterns=["*.msgpack", "*.h5", "*.ot"] 
)
print(f"✅ Audio model downloaded to {CACHE_DIR}")
