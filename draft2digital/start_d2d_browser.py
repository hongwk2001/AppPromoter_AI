"""
start_d2d_browser.py
Launches an independent Chromium browser window on your desktop for Draft2Digital.
"""

import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = r"C:\tmp\d2d_chromium_profile"
os.makedirs(PROFILE_DIR, exist_ok=True)

def run_browser():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--remote-debugging-port=9222"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.draft2digital.com")
        print("✅ Chromium window active at https://www.draft2digital.com (Port 9222)")
        
        while True:
            time.sleep(1)

if __name__ == "__main__":
    if "--runner" in sys.argv:
        run_browser()
    else:
        # Spawn as detached console window
        script = os.path.abspath(__file__)
        cmd = [sys.executable, script, "--runner"]
        proc = subprocess.Popen(cmd, creationflags=0x00000010) # CREATE_NEW_CONSOLE
        print(f"🚀 Launched detached Chromium window (PID: {proc.pid})")
