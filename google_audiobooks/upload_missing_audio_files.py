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

def upload_missing_tracks(book_name, lang="ko", port=9222):
    meta_path = os.path.join(NOTES_DIR, f"google_audio_metadata_{book_name}_{lang}.json")
    if not os.path.exists(meta_path):
        print(f"Error: Could not load metadata JSON for {book_name}")
        return

    with open(meta_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_audio_files = data.get("content_files", {}).get("audio_files", [])
    if not all_audio_files:
        print("Error: No audio files found in metadata.")
        return

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error connecting to CDP port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        print(f"Connected to page: {page.url} ({page.title()})")

        # Get list of already uploaded filenames on page
        uploaded_names = page.evaluate("""
        () => {
            const txt = document.body.innerText || '';
            const match = txt.match(/([a-zA-Z0-9_\\-]+\\.(mp3|jpg|png))/g) || [];
            return Array.from(new Set(match));
        }
        """)

        missing_files = [f for f in all_audio_files if os.path.basename(f) not in uploaded_names]

        print(f"\n📊 Total Audio Tracks in Metadata: {len(all_audio_files)}")
        print(f"  ✓ Already Uploaded on Page: {len(all_audio_files) - len(missing_files)}")
        print(f"  ➡️ Missing Tracks to Upload: {len(missing_files)}\n")

        if not missing_files:
            print("🎉 ALL audio tracks are already uploaded! Nothing to do.")
            return

        # Divide missing files into ~30MB batches
        batches = []
        current_batch = []
        current_size = 0
        MAX_BATCH = 30 * 1024 * 1024

        for fpath in missing_files:
            fsize = os.path.getsize(fpath)
            if current_batch and (current_size + fsize > MAX_BATCH):
                batches.append(current_batch)
                current_batch = [fpath]
                current_size = fsize
            else:
                current_batch.append(fpath)
                current_size += fsize
        if current_batch:
            batches.append(current_batch)

        print(f"➡️ Split {len(missing_files)} missing files into {len(batches)} batches.\n")

        for idx, batch in enumerate(batches, 1):
            print(f"➡️ Batch [{idx}/{len(batches)}] ({len(batch)} files): {[os.path.basename(b) for b in batch]}")

            # 1. Close modal if open
            page.keyboard.press("Escape")
            time.sleep(0.5)
            close_btn = page.locator('mat-dialog-container button:has-text("Close")')
            if close_btn.count() > 0 and close_btn.first.is_visible():
                close_btn.first.click(force=True)
                time.sleep(1.5)

            # 2. Click "Upload audio file" button
            upload_btn = page.locator('button:has-text("Upload audio file"), [role="button"]:has-text("Upload audio file")').first
            if upload_btn.count() > 0:
                upload_btn.click(force=True)
                time.sleep(2)

            # 3. Trigger Browse button to initialize file input
            browse_btn = page.locator('mat-dialog-container button[xapuploadertrigger], mat-dialog-container button:has-text("Browse")').first
            if browse_btn.count() > 0:
                browse_btn.click(force=True)
                time.sleep(1)

            # 4. Attach files to input[type="file"]
            file_inp = page.locator('input[type="file"]').first
            if file_inp.count() > 0:
                file_inp.set_input_files(batch)
                print(f"  ✅ Batch [{idx}/{len(batches)}] successfully attached into upload queue!")
                time.sleep(4)
            else:
                print(f"  ⚠️ file input element not found for batch {idx}")

        # Final cleanup
        close_btn = page.locator('mat-dialog-container button:has-text("Close")')
        if close_btn.count() > 0 and close_btn.first.is_visible():
            close_btn.first.click(force=True)

        print("\n✨ Missing Audio Tracks Upload Completed!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", type=str, default="beowulf")
    parser.add_argument("--lang", type=str, default="ko")
    args = parser.parse_args()

    upload_missing_tracks(args.book, args.lang)
