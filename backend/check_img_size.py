from PIL import Image
import os

file_path = "uploads/images/6da357b7-2f42-4a2a-a972-6e66b1becb75.jpg"
if os.path.exists(file_path):
    img = Image.open(file_path)
    print(f"Image Size: {img.size}")
    print(f"Format: {img.format}")
else:
    print("File not found.")
