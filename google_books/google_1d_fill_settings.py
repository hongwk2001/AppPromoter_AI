"""
google_1d_fill_settings.py
Switches to Settings sub-tab (#book/.../info/settings) on Google Books Partner Center,
populates DRM settings, preview limit, and copy/paste limit based on book metadata JSON.
STOPS immediately after filling for user review — does NOT click Save & Continue.
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

def fill_settings_tab(book_name, lang="ko", port=9222):
    data = load_google_metadata(book_name, lang)
    if not data:
        print("Error: Could not load Google Books metadata.")
        return

    settings_cfg = data.get("tab5_settings", {
        "enable_drm": True,
        "preview_percentage": "20"
    })
    enable_drm = settings_cfg.get("enable_drm", True)
    preview_pct = str(settings_cfg.get("preview_percentage", "20")) + "%"

    print(f"\n📋 Filling Google Books Settings sub-tab for: {book_name} ({lang.upper()})")
    print(f"  Enable DRM:     {enable_drm}")
    print(f"  Preview Limit:  {preview_pct}")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "info/" in pg.url]
        if not pages:
            pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        # 1. Switch to Settings sub-tab if needed
        if "info/settings" not in page.url:
            settings_tab = page.locator('a:has-text("Settings"), span:has-text("Settings"), div[role="tab"]:has-text("Settings")')
            if settings_tab.count() > 0:
                print("➡️ Clicking 'Settings' sub-tab...")
                settings_tab.first.click()
                time.sleep(2)

        print(f"Active Page: {page.url} ({page.title()})")

        # 2. Select DRM Option
        drm_target = "Yes" if enable_drm else "No"
        drm_field = page.locator('mat-form-field:has-text("DRM") mat-select, mat-form-field:has-text("encryption") mat-select').first
        if drm_field.count() > 0:
            drm_field.click()
            time.sleep(1)
            opt = page.locator(f'mat-option:has-text("{drm_target}")').first
            if opt.count() > 0:
                opt.click()
                print(f"  ✓ Set DRM Encryption to: {drm_target}")
                time.sleep(1)

        # 3. Select Preview Limit Option
        prev_field = page.locator('mat-form-field:has-text("Preview limit") mat-select').first
        if prev_field.count() > 0:
            prev_field.click()
            time.sleep(1)
            opt = page.locator(f'mat-option:has-text("{preview_pct}")').first
            if opt.count() > 0:
                opt.click()
                print(f"  ✓ Set Preview Limit to: {preview_pct}")
                time.sleep(1)

        # Blur active element
        if page.evaluate("document.activeElement"):
            page.evaluate("document.activeElement.blur()")

        print("\n✨ Settings Sub-tab Populated! (Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill Google Books Settings Sub-tab & Pause for Review")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    fill_settings_tab(args.book, args.lang, port=args.port)
