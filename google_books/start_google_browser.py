"""
start_google_browser.py
Launches an independent visible Chrome browser window on port 9222
and opens Google Books Partner Center (https://play.google.com/books/publish/).
"""

import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROFILE_DIR = r"C:\tmp\google_books_chrome_profile"
os.makedirs(PROFILE_DIR, exist_ok=True)

def run_browser():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1300, "height": 900},
            args=["--remote-debugging-port=9222"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://play.google.com/books/publish/")
        print("✅ Launched visible Chrome window on Port 9222 at https://play.google.com/books/publish/")
        
        while True:
            time.sleep(1)

if __name__ == "__main__":
    if "--runner" in sys.argv:
        run_browser()
    else:
        script = os.path.abspath(__file__)
        cmd = [sys.executable, script, "--runner"]
        proc = subprocess.Popen(cmd, creationflags=0x00000010) # CREATE_NEW_CONSOLE
        print(f"🚀 Launched detached Chrome window for Google Books Partner (PID: {proc.pid})")
