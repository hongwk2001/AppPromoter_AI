"""
automate_ar_feedback_fix.py
Automates resubmission fixes on Authors Republic for both:
  1. Korean Edition (projectId=73506) - Cover image replacement + Closing track fix
  2. English Edition (projectId=73477) - Public Domain radio selection + Closing track fix
"""

import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BOOK_DIR = r"C:\git_repo\TKprof_book\books\the_enchanted_april"
KO_COVER = os.path.join(BOOK_DIR, "cover_ko_audio_2400.jpg")
# The English cover gained a "Narrated by TKPROF AI" line on 2026-09-20;
# AR requires the narrator to match across cover, metadata and tracks.
EN_COVER = os.path.join(BOOK_DIR, "cover_en_audio_2400.jpg")
KO_AUDIO_DIR = os.path.join(BOOK_DIR, "final_audio_ko_ready")
EN_AUDIO_DIR = os.path.join(BOOK_DIR, "final_audio_en_ar")

# Accepting the distribution agreement is a human decision, so Tab 4 is
# off by default. Set True only when you mean to submit unattended.
SUBMIT_TAB4 = False

def resubmit_project(page, project_id, is_korean=True):
    url = f"https://www.authorsrepublic.com/the-republic/projects/publish-a-book?projectId={project_id}"
    print(f"\n======================================================================")
    print(f"🚀 Processing Authors Republic Resubmission for Project ID: {project_id}")
    print(f"======================================================================")
    page.goto(url)
    page.wait_for_load_state("networkidle")
    time.sleep(2.0)

    # -------------------------------------------------------------------------
    # TAB 2: METADATA (For English Edition - Check Public Domain = Yes)
    # -------------------------------------------------------------------------
    if not is_korean:
        print("\n--- Navigating to Tab 2 (Metadata) for English Edition ---")
        tabs = page.query_selector_all(".w-20, ul.nav-tabs li, nav a")
        if len(tabs) >= 2:
            tabs[1].click()
            time.sleep(2.0)

        print("Setting Public Domain = Yes (#PublicDomainYes / radio)...")
        if page.is_visible("#PublicDomainYes"):
            page.click("#PublicDomainYes")
        else:
            # Check by input evaluate
            page.evaluate("""() => {
                const radios = Array.from(document.querySelectorAll('input[type="radio"]'));
                const pdYes = radios.find(r => r.name.includes('PublicDomain') && (r.value === 'true' || r.id.includes('Yes')));
                if (pdYes) pdYes.click();
            }""")
        time.sleep(0.5)

        print("Saving Tab 2 (#SaveContinue)...")
        if page.is_visible("#SaveContinue"):
            page.click("#SaveContinue")
            time.sleep(3.0)

    # -------------------------------------------------------------------------
    # TAB 3: AUDIO & COVER ART
    # -------------------------------------------------------------------------
    print("\n--- Navigating to Tab 3 (Audio & Cover Art) ---")
    tabs = page.query_selector_all(".w-20, ul.nav-tabs li, nav a")
    if len(tabs) >= 3:
        tabs[2].click()
        time.sleep(2.0)

    # 1. Replace Cover Image
    cover = KO_COVER if is_korean else EN_COVER
    if os.path.exists(cover):
        print(f"Uploading 2400x2400 Cover Image: {cover}")
        try:
            with page.expect_file_chooser(timeout=3000) as fc_info:
                page.click(".cover-select label", force=True)
            fc_info.value.set_files(cover)
            print("✅ Cover image set via file chooser!")
        except Exception as e:
            print(f"  Fallback direct input set: {e}")
            page.set_input_files("#square-cover-file", cover, timeout=120000)
        time.sleep(3.0)

    # 2. Audio Uploads
    target_dir = KO_AUDIO_DIR if is_korean else EN_AUDIO_DIR
    inputs = page.query_selector_all("input.chunkUploader")
    print(f"Found {len(inputs)} chunkUploader inputs on Tab 3.")

    # Opening Track -- inputs[0] was left empty on every previous run
    opening_path = os.path.join(target_dir, "final_track_00_intro.mp3")
    if len(inputs) >= 1 and os.path.exists(opening_path):
        print(f"Uploading Opening Track: {opening_path}")
        inputs[0].set_input_files(opening_path, timeout=120000)
        time.sleep(2.0)

    # Closing Track
    closing_path = os.path.join(target_dir, "closing.mp3")
    if len(inputs) >= 2 and os.path.exists(closing_path):
        print(f"Uploading concise Closing Track: {closing_path}")
        inputs[1].set_input_files(closing_path, timeout=120000)
        time.sleep(2.0)

    # Retail Sample -- inputs[2], never filled on any previous run
    for cand in ("sample.mp3", "sample_retail_3min.mp3"):
        sample_path = os.path.join(target_dir, cand)
        if len(inputs) >= 3 and os.path.exists(sample_path):
            print(f"Uploading Retail Sample: {sample_path}")
            inputs[2].set_input_files(sample_path, timeout=120000)
            time.sleep(2.0)
            break

    # Chapter Tracks
    all_mp3s = sorted([f for f in os.listdir(target_dir) if f.endswith(".mp3")])
    # "intro"/"closing" alone let sample.mp3 and sample_retail_3min.mp3
    # through, and they were uploaded as chapter tracks.
    skip = {"final_track_00_intro.mp3", "closing.mp3",
            "sample.mp3", "sample_retail_3min.mp3"}
    chapter_files = [os.path.join(target_dir, f)
                     for f in all_mp3s if f not in skip]

    if len(inputs) >= 4 and chapter_files:
        print(f"Uploading {len(chapter_files)} Chapter Tracks sequentially...")
        for idx, track_file in enumerate(chapter_files, 1):
            if os.path.exists(track_file):
                file_size_mb = os.path.getsize(track_file) / (1024 * 1024)
                print(f"  [{idx}/{len(chapter_files)}] Uploading {os.path.basename(track_file)} ({file_size_mb:.1f} MB)...")
                try:
                    inputs[3].set_input_files(track_file, timeout=120000)
                    time.sleep(1.5)
                except Exception as e:
                    print(f"    Error uploading {track_file}: {e}")

    # -------------------------------------------------------------------------
    # TAB 4: AGREEMENT & SUBMIT
    # -------------------------------------------------------------------------
    if not SUBMIT_TAB4:
        print("Tab 3 done. Tab 4 (agreement + submit) left for a human.")
        return

    print("\nNavigating to Tab 4 (#AgreementBtn)...")
    if page.is_visible("#AgreementBtn"):
        page.click("#AgreementBtn")
        time.sleep(3.0)

    print("Checking agreement checkboxes on Tab 4...")
    checkboxes = page.query_selector_all("input[type='checkbox']")
    for cb in checkboxes:
        if not cb.is_checked():
            cb.check()
            time.sleep(0.3)

    print(f"\n🎉 Resubmission completed for Project ID: {project_id}")

def run_all_feedback_fixes(edition, port=9222):
    cdp_url = f"http://127.0.0.1:{port}"
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            print(f"❌ Error connecting to Chrome on port {port}: {e}")
            return

        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        if edition in ("ko", "both"):
            resubmit_project(page, "73506", is_korean=True)
        if edition in ("en", "both"):
            resubmit_project(page, "73477", is_korean=False)

if __name__ == "__main__":
    # Korean passed AR validation on 2026-09-20, so re-running it by accident
    # would replace a package that is already accepted. Require the edition.
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg not in ("ko", "en", "both"):
        print("usage: automate_ar_feedback_fix.py ko|en|both")
        sys.exit(1)
    run_all_feedback_fixes(edition=arg)
