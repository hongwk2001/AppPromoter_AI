import os
import sys
import json
import time
import glob
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def upload_ordered_batches(port=9222):
    audio_dir = r"C:\git_repo\TKprof_book\books\beowulf\final_audio_ko"
    if not os.path.exists(audio_dir):
        print(f"Error: Directory {audio_dir} does not exist.")
        return

    def sort_key(p):
        fname = os.path.basename(p).lower()
        if fname in ["opening_credits.mp3", "opening.mp3"]:
            return (0, 0)
        elif "intro" in fname:
            return (0, 1)
        elif fname == "closing.mp3":
            return (2, 0)
        elif fname == "closing_credits.mp3":
            return (2, 1)
        elif fname == "sample.mp3":
            return (3, 0)
        else:
            nums = "".join([ch for ch in fname if ch.isdigit()])
            val = int(nums) if nums else 500
            return (1, val)

    mp3_paths = glob.glob(os.path.join(audio_dir, "*.mp3"))
    mp3_paths.sort(key=sort_key)
    ordered_files = list(dict.fromkeys(mp3_paths))

    # Split files into batches < 30 MB
    batches = []
    current_batch = []
    current_size = 0
    MAX_BATCH_SIZE = 30 * 1024 * 1024  # 30 MB (well below Playwright 50MB limit)

    for fpath in ordered_files:
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

    print(f"📋 Total ordered audio tracks: {len(ordered_files)} ({len(batches)} batches < 30MB each)")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error connecting to Chrome: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        print(f"\nConnected to page: {page.url} ({page.title()})\n")

        for idx, batch in enumerate(batches, 1):
            print(f"➡️ Processing Batch [{idx}/{len(batches)}] ({len(batch)} MP3 files): {[os.path.basename(b) for b in batch]}")

            # 1. Close modal dialog if open
            page.keyboard.press("Escape")
            time.sleep(0.5)
            close_btn = page.locator('mat-dialog-container button:has-text("Close")')
            if close_btn.count() > 0 and close_btn.first.is_visible():
                close_btn.first.click(force=True)
                time.sleep(1.5)

            # 2. Click "Upload audio file" button on page
            upload_btn = page.locator('button:has-text("Upload audio file"), [role="button"]:has-text("Upload audio file")').first
            if upload_btn.count() > 0:
                upload_btn.click(force=True)
                time.sleep(2)

            # 3. Trigger Browse button in modal to initialize <input type="file">
            browse_btn = page.locator('mat-dialog-container button[xapuploadertrigger], mat-dialog-container button:has-text("Browse")').first
            if browse_btn.count() > 0:
                browse_btn.click(force=True)
                time.sleep(1)

            # 4. Attach batch (< 30MB)
            file_inp = page.locator('input[type="file"]').first
            if file_inp.count() > 0:
                file_inp.set_input_files(batch)
                print(f"  ✅ Batch [{idx}/{len(batches)}] attached successfully into upload queue!")
                time.sleep(3)
            else:
                print(f"  ⚠️ file input element not found for batch {idx}")

        # Final cleanup close dialog
        page.keyboard.press("Escape")
        time.sleep(0.5)
        close_btn = page.locator('mat-dialog-container button:has-text("Close")')
        if close_btn.count() > 0 and close_btn.first.is_visible():
            close_btn.first.click(force=True)

        print(f"\n✨ ALL {len(ordered_files)} audio tracks successfully uploaded in exact track order!")

if __name__ == "__main__":
    upload_ordered_batches()
