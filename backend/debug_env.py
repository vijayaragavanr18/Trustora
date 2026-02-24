import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Path: {sys.path}")
try:
    import torch
    print(f"Torch Version: {torch.__version__}")
except Exception as e:
    print(f"Torch Import Error: {e}")
