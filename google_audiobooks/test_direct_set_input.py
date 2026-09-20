import time
import os
import sys
import glob
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_direct_set():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "content" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        audio_dir = r"C:\git_repo\TKprof_book\books\blue_castle\final_audio_ko"
        mp3_files = glob.glob(os.path.join(audio_dir, "*.mp3"))
        
        def sort_key(p):
            fname = os.path.basename(p)
            if "intro" in fname:
                return (0, 0)
            elif "closing" in fname:
                return (2, 9999)
            else:
                nums = "".join([ch for ch in fname if ch.isdigit()])
                return (1, int(nums) if nums else 500)

        mp3_files.sort(key=sort_key)
        print(f"Targeting input[type='file'] with {len(mp3_files)} MP3 files...")

        file_inp = page.locator('input[type="file"]').first
        if file_inp.count() > 0:
            print("Found input[type='file'] element:", file_inp.evaluate("el => el.outerHTML"))
            file_inp.set_input_files(mp3_files)
            print(f"✅ Successfully set {len(mp3_files)} audio files directly on input element!")
            time.sleep(2)

if __name__ == "__main__":
    test_direct_set()
