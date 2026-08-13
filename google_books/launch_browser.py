import os
import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROFILE_DIR = r"C:\tmp\partner_center_profile"

def main():
    print("🚀 Opening Chrome browser window...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1360, "height": 900},
            args=["--remote-debugging-port=9222"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://play.google.com/books/publish/")
        print("✅ Chrome window is now open on your screen!")
        print("💡 You can log in and navigate. Keep this script running in the background.")
        
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()
