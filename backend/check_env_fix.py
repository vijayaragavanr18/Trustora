try:
    import torch
    print(f"Torch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    
    from transformers import ViTForImageClassification
    print("ViTForImageClassification imported successfully.")
except Exception as e:
    print(f"Check Failed: {e}")
    import traceback
    traceback.print_exc()
