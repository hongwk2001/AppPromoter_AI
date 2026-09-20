import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def test_upload():
    payload_path = os.path.join(NOTES_DIR, "ar_payload_blue_castle_ko.json")
    with open(payload_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

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

        # 1. Cover Image Upload
        cover_path = payload['cover_path']
        if os.path.exists(cover_path):
            print(f"Uploading Cover Image: {cover_path}")
            page.set_input_files("#square-cover-file", cover_path)
            time.sleep(2.0)

        # 2. Get all chunkUploader input elements
        inputs = page.query_selector_all("input.chunkUploader")
        print(f"Found {len(inputs)} chunkUploader inputs.")

        # inputs[0]: Opening Track
        if len(inputs) >= 1 and payload.get('opening_track') and os.path.exists(payload['opening_track']):
            print(f"Uploading Opening Track: {payload['opening_track']}")
            inputs[0].set_input_files(payload['opening_track'])
            time.sleep(2.0)

        # inputs[1]: Closing Track
        if len(inputs) >= 2 and payload.get('closing_track') and os.path.exists(payload['closing_track']):
            print(f"Uploading Closing Track: {payload['closing_track']}")
            inputs[1].set_input_files(payload['closing_track'])
            time.sleep(2.0)

        # inputs[2]: Sample Track
        if len(inputs) >= 3 and payload.get('sample_track') and os.path.exists(payload['sample_track']):
            print(f"Uploading Sample Track: {payload['sample_track']}")
            inputs[2].set_input_files(payload['sample_track'])
            time.sleep(2.0)

        # inputs[3]: Chapter Tracks (Multiple)
        chapter_files = [f for f in payload['audio_tracks'] if "intro" not in f and "closing" not in f]
        if len(inputs) >= 4 and chapter_files:
            print(f"Uploading {len(chapter_files)} Chapter Tracks...")
            inputs[3].set_input_files(chapter_files)
            time.sleep(5.0)

        print("\n✅ File upload trigger completed. Checking upload progress modal or state...")

if __name__ == "__main__":
    test_upload()
