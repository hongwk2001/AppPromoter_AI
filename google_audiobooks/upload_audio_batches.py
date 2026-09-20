import os
import sys
import json
import time
import glob
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

def upload_all_audio_tracks(book_name, lang="ko", port=9222):
    data = load_audio_metadata(book_name, lang)
    if not data:
        print("Error: Could not load Audiobook metadata.")
        return

    content = data.get("content_files", {})
    audio_files = content.get("audio_files", [])
    if not audio_files:
        print("Error: No audio files found in metadata.")
        return

    print(f"\n📋 Batch Uploading {len(audio_files)} Audio MP3 Files for: {book_name} ({lang.upper()})")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        if "/content" not in page.url:
            base_book_url = page.url.split("#")[0]
            fragment = page.url.split("#")[1] if "#" in page.url else ""
            book_id = fragment.split(";")[0] if fragment else "book/GGKEY:36XB0RU25C2"
            content_url = f"{base_book_url}#{book_id};jc=true/content"
            print(f"➡️ Navigating to Content tab: {content_url}")
            page.goto(content_url)
            time.sleep(2)

        # Dismiss any open modal dialog first
        close_btn = page.locator('mat-dialog-container button:has-text("Close")')
        if close_btn.count() > 0 and close_btn.first.is_visible():
            close_btn.first.click(force=True)
            time.sleep(1)

        # Click "Upload audio file" button
        upload_btn = page.locator('button:has-text("Upload audio file"), [role="button"]:has-text("Upload audio file")').first
        if upload_btn.count() > 0 and upload_btn.is_visible():
            print("➡️ Opening 'Upload audio file' modal dialog...")
            upload_btn.click(force=True)
            time.sleep(1.5)

        # Trigger Browse button inside modal to initialize <input type="file">
        browse_btn = page.locator('mat-dialog-container button[xapuploadertrigger], mat-dialog-container button:has-text("Browse")').first
        if browse_btn.count() > 0:
            print("  ✓ Triggering Browse input initialization...")
            browse_btn.click(force=True)
            time.sleep(1)

        # Divide 49 files into 35MB batches
        batches = []
        current_batch = []
        current_size = 0
        MAX_BATCH_SIZE = 35 * 1024 * 1024  # 35 MB per batch

        for fpath in audio_files:
            fsize = os.path.getsize(fpath)
            if current_batch and (current_size + fsize > MAX_BATCH_SIZE):
                batches.append(current_batch)
                current_batch = [fpath]
                current_size = fsize
            else:
                current_batch.append(fpath)
                current_size += fsize
        if current_batch:
            batches.append(current_batch)

        print(f"➡️ Preparing to queue {len(audio_files)} audio files via CDP DOM.setFileInputFiles...")

        # Ensure modal dialog is open and Browse button clicked to generate input[type="file"]
        file_inp = page.locator('input[type="file"]').first
        if file_inp.count() == 0:
            add_more_btn = page.locator('mat-dialog-container button:has-text("Browse"), mat-dialog-container button:has-text("Add more files"), mat-dialog-container button:has-text("Add files")').first
            if add_more_btn.count() > 0:
                print("  ➡️ Triggering Browse button to generate file input...")
                add_more_btn.click(force=True)
                time.sleep(1.5)

        # Connect CDP session directly with the page to set files natively without size limits
        client = page.context.new_cdp_session(page)
        doc = client.send("DOM.getDocument")
        node = client.send("DOM.querySelector", {
            "nodeId": doc["root"]["nodeId"],
            "selector": 'input[type="file"]'
        })

        node_id = node.get("nodeId")
        if node_id and node_id > 0:
            print(f"  ✓ Found DOM Node ID {node_id} for input[type='file']")
            print(f"  ➡️ Native CDP setFileInputFiles queued for all {len(audio_files)} MP3 audio files...")
            client.send("DOM.setFileInputFiles", {
                "files": audio_files,
                "nodeId": node_id
            })

            # Dispatch change & input events on input element
            page.evaluate("""
            () => {
                const inp = document.querySelector('input[type="file"]');
                if (inp) {
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
            """)
            print(f"\n✅ ALL {len(audio_files)} audio track files successfully set into Google Books Uploader!")
            time.sleep(3)
        else:
            print("  ❌ Could not locate input[type='file'] DOM node via CDP.")
        time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload ALL Audiobook MP3 Tracks in Batches")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    upload_all_audio_tracks(args.book, args.lang, port=args.port)
