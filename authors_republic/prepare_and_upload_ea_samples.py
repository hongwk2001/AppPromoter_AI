"""
prepare_and_upload_ea_samples.py
Creates exact 3.0-minute retail sample tracks for both Korean and English editions of The Enchanted April,
and uploads them directly to chunkUploader[2] (Sample Track field) on Authors Republic for project IDs 73506 and 73477.
"""

import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BOOK_DIR = r"C:\git_repo\TKprof_book\books\the_enchanted_april"

def slice_3min_sample(src_mp3, out_mp3):
    cmd = [
        "ffmpeg", "-y",
        "-ss", "0",
        "-t", "180",
        "-i", src_mp3,
        "-c", "copy",
        out_mp3
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", out_mp3], capture_output=True, text=True).stdout.strip())
    size_mb = os.path.getsize(out_mp3) / (1024 * 1024)
    print(f"  ✅ Sliced Sample: {out_mp3} | Duration: {dur:.1f}s ({dur/60.0:.2f} mins) | Size: {size_mb:.2f} MB")
    return out_mp3

def upload_sample_to_project(page, project_id, sample_file):
    url = f"https://www.authorsrepublic.com/the-republic/projects/publish-a-book?projectId={project_id}"
    print(f"\n======================================================================")
    print(f"🎙️ Uploading Retail Sample Track to Project ID: {project_id}")
    print(f"======================================================================")
    page.goto(url)
    page.wait_for_load_state("networkidle")
    time.sleep(2.0)

    # Click Tab 3 (Audio & Cover Art)
    tabs = page.query_selector_all(".w-20, ul.nav-tabs li, nav a")
    if len(tabs) >= 3:
        print("Navigating to Tab 3 (Audio & Cover Art)...")
        tabs[2].click()
        time.sleep(2.0)

    inputs = page.query_selector_all("input.chunkUploader")
    print(f"Found {len(inputs)} chunkUploader inputs on Tab 3.")

    if len(inputs) >= 3:
        print(f"Uploading Sample Track to chunkUploader[2]: {sample_file}")
        inputs[2].set_input_files(sample_file, timeout=120000)
        time.sleep(4.0)
        print("✅ Retail sample track upload triggered successfully!")

    # Click Tab 4 (#AgreementBtn) & Save
    if page.is_visible("#AgreementBtn"):
        print("Navigating to Tab 4 (#AgreementBtn)...")
        page.click("#AgreementBtn")
        time.sleep(2.5)

    checkboxes = page.query_selector_all("input[type='checkbox']")
    for cb in checkboxes:
        if not cb.is_checked():
            cb.check()
            time.sleep(0.3)

    print(f"🎉 Sample track attachment completed for Project ID: {project_id}")

def main():
    ko_src = os.path.join(BOOK_DIR, "final_audio_ko", "final_track_01.mp3")
    ko_sample_out = os.path.join(BOOK_DIR, "final_audio_ko_ready", "sample_retail_3min.mp3")

    en_src = os.path.join(BOOK_DIR, "final_audio", "final_track_01.mp3")
    en_sample_out = os.path.join(BOOK_DIR, "final_audio_ready", "sample_retail_3min.mp3")

    print("--- [1] Preparing Korean Retail Sample ---")
    slice_3min_sample(ko_src, ko_sample_out)

    print("\n--- [2] Preparing English Retail Sample ---")
    slice_3min_sample(en_src, en_sample_out)

    print("\n--- [3] Uploading Sample Tracks via Playwright CDP ---")
    cdp_url = "http://127.0.0.1:9222"
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        # 1. Korean Edition (73506)
        upload_sample_to_project(page, "73506", ko_sample_out)

        # 2. English Edition (73477)
        upload_sample_to_project(page, "73477", en_sample_out)

if __name__ == "__main__":
    main()
