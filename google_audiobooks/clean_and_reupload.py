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

def clean_and_reupload(book_name="beowulf", lang="ko", port=9222):
    audio_dir = r"C:\git_repo\TKprof_book\books\beowulf\final_audio_ko"
    if not os.path.exists(audio_dir):
        print(f"Error: Directory {audio_dir} does not exist.")
        return

    # Define exact 1..49 track order
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

    print(f"📋 Total ordered audio tracks to upload: {len(ordered_files)}")
    for idx, f in enumerate(ordered_files, 1):
        print(f"  {idx:02d}. {os.path.basename(f)}")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error connecting to Chrome: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        print(f"\nConnected to page: {page.url} ({page.title()})\n")

        # Dismiss any open modal dialog first
        close_btn = page.locator('mat-dialog-container button:has-text("Close")')
        if close_btn.count() > 0 and close_btn.first.is_visible():
            close_btn.first.click(force=True)
            time.sleep(1.5)

        # 1. Clean up duplicate audio files if delete buttons exist
        print("➡️ Cleaning up existing file rows on page...")
        del_btns = page.locator('tr button:has-text("delete"), mat-row button:has-text("delete"), button[aria-label*="Delete" i]')
        count_del = del_btns.count()
        if count_del > 0:
            print(f"  Found {count_del} delete buttons. Deleting existing file rows...")
            # Click delete buttons from last to first
            for i in range(count_del - 1, -1, -1):
                try:
                    btn = del_btns.nth(i)
                    if btn.is_visible():
                        btn.click(force=True)
                        time.sleep(0.3)
                        # Confirm delete dialog if pops up
                        confirm = page.locator('mat-dialog-container button:has-text("Delete"), mat-dialog-container button:has-text("Remove"), mat-dialog-container button:has-text("Yes")')
                        if confirm.count() > 0 and confirm.first.is_visible():
                            confirm.first.click(force=True)
                            time.sleep(0.3)
                except Exception:
                    pass
            print("  ✓ Cleaned existing file rows.")
            time.sleep(2)

        # 2. Trigger "Upload audio file"
        upload_btn = page.locator('button:has-text("Upload audio file"), [role="button"]:has-text("Upload audio file")').first
        if upload_btn.count() > 0:
            print("➡️ Opening 'Upload audio file' modal dialog...")
            upload_btn.click(force=True)
            time.sleep(2)

        # 3. Initialize <input type="file"> via Browse trigger
        browse_btn = page.locator('mat-dialog-container button[xapuploadertrigger], mat-dialog-container button:has-text("Browse")').first
        if browse_btn.count() > 0:
            print("  ✓ Triggering Browse input initialization...")
            browse_btn.click(force=True)
            time.sleep(1)

        # 4. Pass ALL 49 files in exact ordered sequence to input[type="file"]
        file_inp = page.locator('input[type="file"]').first
        if file_inp.count() > 0:
            print(f"➡️ Attaching ALL {len(ordered_files)} files in exact chronological track order...")
            file_inp.set_input_files(ordered_files)
            print(f"\n✅ SUCCESS! All {len(ordered_files)} audio tracks attached in perfect order!")
            time.sleep(5)
        else:
            print("  ⚠️ input[type='file'] element not found.")

if __name__ == "__main__":
    clean_and_reupload()
