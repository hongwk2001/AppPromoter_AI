"""
capture_d2d_screenshot.py
Captures a screenshot of the active Draft2Digital browser tab and saves it to the artifacts directory.
"""

import os
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ARTIFACT_DIR = r"C:\Users\hongw\.gemini\antigravity\brain\3ffc7a40-51fe-484a-8ebf-a6665ccb000c"
OUTPUT_PATH = os.path.join(ARTIFACT_DIR, "d2d_beowulf_step1_screenshot.png")

def capture():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]
        
        page.screenshot(path=OUTPUT_PATH, full_page=True)
        print(f"✅ Saved screenshot to: {OUTPUT_PATH}")

if __name__ == "__main__":
    capture()
