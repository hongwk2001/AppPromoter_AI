import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def upload_sample():
    payload_path = os.path.join(NOTES_DIR, "ar_payload_blue_castle_ko.json")
    with open(payload_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    sample_track = payload.get("sample_track")
    print(f"Sample Track Path: {sample_track}")
    if not sample_track or not os.path.exists(sample_track):
        print("❌ Sample track file does not exist.")
        return

    cdp_url = "http://127.0.0.1:9222"
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0]
        page = None
        for page_obj in context.pages:
            if "authorsrepublic.com" in page_obj.url:
                page = page_obj
                break
        if not page:
            page = context.pages[0]

        print(f"URL: {page.url}")

        # Find all chunkUploader inputs
        inputs = page.query_selector_all("input.chunkUploader")
        print(f"Found {len(inputs)} chunkUploader inputs on Tab 3.")

        # Index 0: Opening Track
        # Index 1: Closing Track
        # Index 2: Sample Track
        if len(inputs) >= 3:
            print(f"Uploading Sample Track to input index 2: {os.path.basename(sample_track)} ({os.path.getsize(sample_track)/(1024*1024):.1f} MB)...")
            inputs[2].set_input_files(sample_track, timeout=120000)
            time.sleep(3.0)
            print("✅ Sample track upload triggered successfully!")

if __name__ == "__main__":
    upload_sample()
