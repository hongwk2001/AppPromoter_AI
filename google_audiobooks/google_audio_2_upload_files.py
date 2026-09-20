"""
google_audio_2_upload_files.py
Uploads cover_ko.jpg and ALL 47 MP3 audio track files in ONE SHOT for Google Play Books Audiobooks
using native CDP protocol (DOM.setFileInputFiles) to bypass 50MB websocket limits.
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

def load_audio_metadata(book_name, lang="ko"):
    meta_path = os.path.join(NOTES_DIR, f"google_audio_metadata_{book_name}_{lang}.json")
    if not os.path.exists(meta_path):
        from google_audio_0_prepare_metadata import prepare_audio_metadata
        return prepare_audio_metadata(book_name, lang)
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def upload_audio_content(book_name, lang="ko", port=9222):
    data = load_audio_metadata(book_name, lang)
    if not data:
        print("Error: Could not load Audiobook metadata.")
        return

    content = data.get("content_files", {})
    cover_path = content.get("cover_image_path", "")
    audio_files = content.get("audio_files", [])

    print(f"\n📋 Uploading Files to Content Tab for Audiobook: {book_name} ({lang.upper()})")
    print(f"  Cover Image: {cover_path}")
    print(f"  Audio Track MP3 Files: {len(audio_files)} files (ONE-SHOT Upload via CDP)\n")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        # Dismiss any open Angular Material overlays (backdrops, dropdowns)
        page.keyboard.press("Escape")
        time.sleep(0.5)

        # 1. Switch to Content main tab if not active
        if "/content" not in page.url:
            content_tab = page.locator('a[href*="content"], a:has-text("Content"), span:has-text("Content")')
            if content_tab.count() > 0:
                print("➡️ Switching to 'Content' main tab...")
                content_tab.first.click(force=True)
                time.sleep(2)

        print(f"Active Page: {page.url} ({page.title()})")

        def upload_files_to_input(trigger_selector, files_to_attach, label_name):
            # Dismiss any open modal first
            close_btn = page.locator('mat-dialog-container button:has-text("Close")')
            if close_btn.count() > 0 and close_btn.first.is_visible():
                close_btn.first.click(force=True)
                time.sleep(1)

            btn = page.locator(trigger_selector)
            if btn.count() > 0 and btn.first.is_visible():
                print(f"➡️ Opening '{label_name}' modal dialog...")
                btn.first.click(force=True)
                time.sleep(1.5)

            # Click Browse button to initialize input element in DOM
            browse_trigger = page.locator('mat-dialog-container button[xapuploadertrigger], mat-dialog-container button:has-text("Browse")').first
            if browse_trigger.count() > 0:
                print(f"  ✓ Found modal Browse button. Triggering input initialization for {label_name}...")
                browse_trigger.click(force=True)
                time.sleep(1)

            # Connect CDP session directly with page for native zero-limit file injection
            client = page.context.new_cdp_session(page)
            doc = client.send("DOM.getDocument")
            node = client.send("DOM.querySelector", {
                "nodeId": doc["root"]["nodeId"],
                "selector": 'input[type="file"]'
            })
            node_id = node.get("nodeId")

            files_list = [files_to_attach] if isinstance(files_to_attach, str) else files_to_attach
            files_list = list(dict.fromkeys(files_list))

            if node_id and node_id > 0:
                print(f"  ✓ Found DOM Node ID {node_id} for input[type='file']")
                print(f"  ➡️ Native CDP setFileInputFiles queued for {len(files_list)} file(s) ({label_name})...")
                client.send("DOM.setFileInputFiles", {
                    "files": files_list,
                    "nodeId": node_id
                })

                # Dispatch change & input events
                page.evaluate("""
                () => {
                    const inp = document.querySelector('input[type="file"]');
                    if (inp) {
                        inp.dispatchEvent(new Event('input', { bubbles: true }));
                        inp.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
                """)
                print(f"  ✅ {len(files_list)} file(s) for {label_name} queued into Google Books Uploader!")
                time.sleep(3)

        # 1. Upload Cover Image
        if cover_path and os.path.exists(cover_path):
            upload_files_to_input('button:has-text("Upload a cover"), [role="button"]:has-text("Upload a cover")', cover_path, "Upload Cover")

        # 2. Upload ALL Audio Track MP3 Files
        if audio_files:
            upload_files_to_input('button:has-text("Upload audio file"), [role="button"]:has-text("Upload audio file")', audio_files, "Upload Audio Files")

        print("\n✨ Content Tab One-Shot Upload Completed! (Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload Cover & Audio MP3 Tracks in One Shot via CDP")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    upload_audio_content(args.book, args.lang, port=args.port)
