import os
import sys
from PIL import Image

cover_path = r"C:\git_repo\TKprof_book\books\the_enchanted_april\cover_ko.jpg"

if os.path.exists(cover_path):
    with Image.open(cover_path) as img:
        print(f"File: {cover_path}")
        print(f"Size: {os.path.getsize(cover_path)/(1024*1024):.2f} MB")
        print(f"Dimensions: {img.size}")
        print(f"Mode: {img.mode}")
