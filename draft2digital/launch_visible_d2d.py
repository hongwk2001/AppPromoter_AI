"""
launch_visible_d2d.py
Launches a persistent visible Chromium browser window on your desktop.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROFILE_DIR = r"C:\tmp\d2d_chromium_profile"
os.makedirs(PROFILE_DIR, exist_ok=True)

def main():
    with sync_playwright() as p:
        print("🚀 Opening visible browser window for Draft2Digital...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--remote-debugging-port=9222"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://draft2digital.com/book/m/4383546/ebook")
        print("✅ Browser window open at: https://draft2digital.com/book/m/4383546/ebook")
        print("   Listening on CDP port 9222. Press Ctrl+C to close.")
        
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()
