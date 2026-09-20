"""
google_1c_fill_contributors.py
Switches to Tab 3 (Contributors) on Google Books Partner Center,
populates book contributors (H. G. 웰스 as Author, TKPROF LLC as Translator/Editor).
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

def fill_contributors_tab(book_name, lang="ko", port=9222):
    data = load_google_metadata(book_name, lang)
    if not data:
        print("Error: Could not load Google Books metadata.")
        return

    contributors = data.get("tab3_contributors", [
        {"name": "H. G. 웰스", "role": "Author"},
        {"name": "TKPROF LLC", "role": "Translator"}
    ])
    
    print(f"\n📋 Filling Google Books Tab 3 (Contributors) for: {book_name} ({lang.upper()})")

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

        # Dismiss any open Angular Material overlays (backdrops, dropdowns)
        page.keyboard.press("Escape")
        time.sleep(0.5)

        # 1. Switch to Contributors sub-tab if needed
        if "info/contributors" not in page.url:
            contrib_tab = page.locator('a:has-text("Contributors"), span:has-text("Contributors"), div[role="tab"]:has-text("Contributors")')
            if contrib_tab.count() > 0:
                print("➡️ Clicking 'Contributors' sub-tab...")
                contrib_tab.first.click(force=True)
                time.sleep(2)

        print(f"Active Page: {page.url} ({page.title()})")

        # 2. Add each contributor
        # Ensure we are on Contributors sub-tab
        if "/info/contributors" not in page.url:
            contrib_tab = page.locator('a:has-text("Contributors"), span:has-text("Contributors"), div:has-text("Contributors")').first
            if contrib_tab.count() > 0:
                print("➡️ Clicking 'Contributors' sub-tab...")
                contrib_tab.click()
                time.sleep(2)

        for idx, contrib in enumerate(contributors):
            name = contrib.get("name", "")
            role = contrib.get("role", "")
            bio = contrib.get("bio", "")

            # If index > 0, click 'Add a contributor' if row doesn't exist
            if idx > 0:
                name_inps = page.locator('input[placeholder="Name"]')
                if name_inps.count() <= idx:
                    add_btn = page.locator('button:has-text("Add a contributor"), [role="button"]:has-text("Add a contributor")').first
                    if add_btn.count() > 0 and add_btn.is_visible():
                        add_btn.click()
                        time.sleep(1)

            # Target visible Name input
            name_inps = page.locator('input[placeholder="Name"]')
            target_inp = name_inps.nth(idx) if name_inps.count() > idx else name_inps.last
            if target_inp.count() > 0:
                target_inp.focus()
                target_inp.fill(name)
                print(f"  ✓ Filled Name [{idx+1}]: {name}")
                time.sleep(1)

            # Target Role mat-select
            role_selects = page.locator('mat-select')
            target_select = role_selects.nth(idx) if role_selects.count() > idx else role_selects.last
            if target_select.count() > 0:
                target_select.click()
                time.sleep(1)

                role_opt = page.locator(f'mat-option:has-text("{role}"), [role="option"]:has-text("{role}")')
                if role_opt.count() > 0:
                    role_opt.first.click()
                    print(f"  ✓ Selected Role [{idx+1}]: {role}")
                    time.sleep(1)

            # Target Bio rich text editor if bio present
            if bio:
                bio_divs = page.locator('.ql-editor')
                if bio_divs.count() <= idx:
                    add_bio_btns = page.locator('button:has-text("Add biography"), button:has-text("Add bio"), [role="button"]:has-text("Add bio")')
                    if add_bio_btns.count() > 0 and add_bio_btns.last.is_visible():
                        add_bio_btns.last.click()
                        time.sleep(1)
                        bio_divs = page.locator('.ql-editor')

                target_bio = bio_divs.nth(idx) if bio_divs.count() > idx else bio_divs.last
                if target_bio.count() > 0:
                    target_bio.scroll_into_view_if_needed()
                    target_bio.click(force=True)
                    target_bio.evaluate(f'(el) => {{ el.focus(); el.innerHTML = "<p>{bio}</p>"; el.dispatchEvent(new Event("input", {{ bubbles: true }})); el.dispatchEvent(new Event("change", {{ bubbles: true }})); el.dispatchEvent(new Event("blur", {{ bubbles: true }})); }}')
                    print(f"  ✓ Filled & Rendered Author Bio [{idx+1}] ({name})")
                    time.sleep(1)

        print("\n✨ Tab 3 (Contributors) Populated! (Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill Google Books Tab 3 (Contributors) & Pause for Review")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    fill_contributors_tab(args.book, args.lang, port=args.port)
