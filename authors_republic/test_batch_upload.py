import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def test_batched_upload():
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

        print(f"Active Tab URL: {page.url}")

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

        # inputs[3]: Chapter Tracks (Uploaded 1 by 1 or in batches to avoid CDP 50MB limit)
        chapter_files = [f for f in payload['audio_tracks'] if "intro" not in f and "closing" not in f]
        if len(inputs) >= 4 and chapter_files:
            print(f"Uploading {len(chapter_files)} Chapter Tracks 1-by-1...")
            for idx, track_file in enumerate(chapter_files, 1):
                if os.path.exists(track_file):
                    file_size_mb = os.path.getsize(track_file) / (1024 * 1024)
                    print(f"  [{idx}/{len(chapter_files)}] Uploading {os.path.basename(track_file)} ({file_size_mb:.1f} MB)...")
                    try:
                        inputs[3].set_input_files(track_file)
                        time.sleep(1.5)
                    except Exception as e:
                        print(f"    Error uploading {track_file}: {e}")

        print("\n✅ All chapter tracks batch upload submitted cleanly!")

if __name__ == "__main__":
    test_batched_upload()
