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

def upload_all_batches(book_name, lang="ko", port=9222):
    data = load_audio_metadata(book_name, lang)
    if not data:
        print("Error: Could not load Audiobook metadata.")
        return

    content = data.get("content_files", {})
    audio_files = content.get("audio_files", [])
    if not audio_files:
        print("Error: No audio files found.")
        return

    # Split 49 files into ~35MB batches
    batches = []
    current_batch = []
    current_size = 0
    MAX_BATCH_SIZE = 35 * 1024 * 1024  # 35 MB

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

    print(f"\n📋 Sequential Batch Uploading {len(audio_files)} MP3 Files ({len(batches)} batches) for: {book_name}")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        for idx, batch in enumerate(batches, 1):
            print(f"\n➡️ Processing Batch [{idx}/{len(batches)}] ({len(batch)} files)...")

            # 1. Close any open modal dialog first
            close_btn = page.locator('mat-dialog-container button:has-text("Close")')
            if close_btn.count() > 0 and close_btn.first.is_visible():
                print("  ✓ Closing existing modal dialog...")
                close_btn.first.click(force=True)
                time.sleep(1.5)

            # 2. Click "Upload audio file" button on page
            upload_btn = page.locator('button:has-text("Upload audio file"), [role="button"]:has-text("Upload audio file")').first
            if upload_btn.count() > 0:
                upload_btn.click(force=True)
                time.sleep(1.5)

            # 3. Click Browse button inside modal to initialize <input type="file">
            browse_btn = page.locator('mat-dialog-container button[xapuploadertrigger], mat-dialog-container button:has-text("Browse")').first
            if browse_btn.count() > 0:
                browse_btn.click(force=True)
                time.sleep(1)

            # 4. Target file input and set files
            file_inp = page.locator('input[type="file"]').first
            if file_inp.count() > 0:
                file_inp.set_input_files(batch)
                print(f"  ✅ Batch [{idx}/{len(batches)}] queued successfully!")
                time.sleep(2)
            else:
                print(f"  ⚠️ Could not find file input for batch {idx}")

        # Final cleanup close
        close_btn = page.locator('mat-dialog-container button:has-text("Close")')
        if close_btn.count() > 0 and close_btn.first.is_visible():
            close_btn.first.click(force=True)

        print(f"\n✨ ALL {len(audio_files)} MP3 audio files uploaded across all {len(batches)} batches!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko")
    args = parser.parse_args()

    upload_all_batches(args.book, args.lang)
