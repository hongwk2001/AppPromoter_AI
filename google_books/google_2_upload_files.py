"""
google_2_upload_files.py
Switches to Content tab on Google Books Partner Center and attaches EPUB & Cover image.
STOPS immediately after attaching for user review — does NOT click Save & Continue or Submit.
"""

import os
import sys
import json
import time
import argparse
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def load_google_metadata(book_name, lang="ko"):
    meta_path = os.path.join(NOTES_DIR, f"google_metadata_{book_name}_{lang}.json")
    if not os.path.exists(meta_path):
        from google_0_prepare_metadata import prepare_google_metadata
        return prepare_google_metadata(book_name, lang)
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def upload_content_files(book_name, lang="ko", port=9222):
    data = load_google_metadata(book_name, lang)
    if not data:
        print("Error: Could not load Google Books metadata.")
        return

    files = data.get("files", {})
    epub_path = files.get("epub_path", "")
    cover_path = files.get("cover_path", "")
    upload_list = [f for f in [epub_path, cover_path] if os.path.exists(f)]

    print(f"\n📋 Uploading Files to Content Tab for: {book_name} ({lang.upper()})")
    print(f"  EPUB Manuscript: {epub_path}")
    print(f"  Cover Image:     {cover_path}\n")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "/content" in pg.url]
        if not pages:
            pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        # 1. Switch to Content main tab if not active
        if "/content" not in page.url:
            content_tab = page.locator('a:has-text("Content"), span:has-text("Content"), div:has-text("Content")')
            if content_tab.count() > 0:
                print("➡️ Switching to 'Content' main tab...")
                content_tab.first.click()
                time.sleep(2)

        print(f"Active Page: {page.url} ({page.title()})")

        # 2. Register filechooser event listener
        def on_file_chooser(file_chooser):
            print("  ✓ Triggered File Chooser! Attaching files...")
            file_chooser.set_files(upload_list)
            for f in upload_list:
                print(f"    - {os.path.basename(f)}")

        page.on("filechooser", on_file_chooser)

        # 3. Click 'Upload a file' button
        upload_btn = page.locator('button:has-text("Upload a file"), button:has-text("Upload"), [role="button"]:has-text("Upload a file")').first
        if upload_btn.count() > 0:
            print("➡️ Clicking 'Upload a file' button...")
            upload_btn.click()
            time.sleep(3)

        print("\n✨ Content Tab Files Attached! (Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload Files on Google Books Content Tab & Pause for Review")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    upload_content_files(args.book, args.lang, port=args.port)
