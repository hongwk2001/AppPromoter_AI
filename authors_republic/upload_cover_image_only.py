import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def upload_cover(book_name="beowulf"):
    payload_path = os.path.join(NOTES_DIR, f"ar_payload_{book_name}_ko.json")
    if not os.path.exists(payload_path):
        payload_path = os.path.join(NOTES_DIR, "ar_payload_blue_castle_ko.json")
    with open(payload_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    cover_path = payload.get("cover_path")
    print(f"Cover Image Path: {cover_path}")
    if not cover_path or not os.path.exists(cover_path):
        print("❌ Cover image file does not exist.")
        return

    file_size_mb = os.path.getsize(cover_path) / (1024 * 1024)
    print(f"Cover file size: {file_size_mb:.2f} MB")

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

        # Check if #square-cover-file exists
        cover_input = page.query_selector("#square-cover-file")
        if cover_input:
            print("Found #square-cover-file input. Uploading cover image...")
            page.set_input_files("#square-cover-file", cover_path, timeout=120000)
            time.sleep(3.0)
            print("✅ Cover image upload triggered successfully!")
        else:
            print("❌ #square-cover-file input not found on active page.")

if __name__ == "__main__":
    upload_cover()
