"""
google_1b_fill_genres.py
Automates populating the Genres sub-tab on Google Books Partner Center:
- For Korean books ('lang=ko'): Selects 'GKSS (Korean)' scheme and adds '(102) 영미소설' & '(106) 동서양고전'.
- For English books ('lang=en'): Selects 'BISAC (North America)' scheme and adds 'FICTION / Classics' & 'FICTION / Satire'.
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

GKSS_PRESETS = {
    "tono_bungay": [
        {"code": "102", "name": "영미소설"},
        {"code": "106", "name": "동서양고전"},
        {"code": "100", "name": "소설"}
    ],
    "gilgamesh": [
        {"code": "106", "name": "동서양고전"},
        {"code": "100", "name": "소설"},
        {"code": "108", "name": "역사소설"}
    ],
    "the_enchanted_april": [
        {"code": "102", "name": "영미소설"},
        {"code": "106", "name": "동서양고전"},
        {"code": "100", "name": "소설"}
    ],
    "secret_garden": [
        {"code": "102", "name": "영미소설"},
        {"code": "106", "name": "동서양고전"},
        {"code": "100", "name": "소설"}
    ],
    "odyssey": [
        {"code": "106", "name": "동서양고전"},
        {"code": "102", "name": "영미소설"},
        {"code": "100", "name": "소설"}
    ]
}

def load_google_metadata(book_name, lang="ko"):
    meta_path = os.path.join(NOTES_DIR, f"google_metadata_{book_name}_{lang}.json")
    if not os.path.exists(meta_path):
        from google_0_prepare_metadata import prepare_google_metadata
        return prepare_google_metadata(book_name, lang)
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def fill_genres_tab(book_name, lang="ko", port=9222):
    data = load_google_metadata(book_name, lang)
    if not data:
        print("Error: Could not load Google Books metadata.")
        return

    print(f"\n📋 Filling Google Books Tab 2 (Genres) for: {book_name} ({lang.upper()})")

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

        # 1. Switch to Genres sub-tab if needed
        if "info/genres" not in page.url:
            genre_tab = page.locator('a:has-text("Genres"), span:has-text("Genres"), div[role="tab"]:has-text("Genres")')
            if genre_tab.count() > 0:
                print("➡️ Clicking 'Genres' sub-tab...")
                genre_tab.first.click()
                time.sleep(2)

        print(f"Active Page: {page.url} ({page.title()})")

        # 2. Add each category
        categories = GKSS_PRESETS.get(book_name, ["영미소설", "동서양고전"]) if lang == "ko" else ["FICTION / Classics", "FICTION / Satire"]
        
        for cat_info in categories:
            code = cat_info.get("code", cat_info) if isinstance(cat_info, dict) else cat_info
            name = cat_info.get("name", "") if isinstance(cat_info, dict) else ""

            # Click '+ Add a genre'
            add_btn = page.locator('button:has-text("Add a genre"), [role="button"]:has-text("Add a genre")').first
            if add_btn.count() > 0:
                add_btn.click()
                time.sleep(1)

            # Select scheme on new row
            mat_selects = page.locator('mat-select')
            if mat_selects.count() > 0:
                target_select = mat_selects.last
                target_select.click()
                time.sleep(1)

                target_scheme = "GKSS" if lang == "ko" else "BISAC"
                gk_opt = page.locator(f'mat-option:has-text("{target_scheme}"), [role="option"]:has-text("{target_scheme}")')
                if gk_opt.count() > 0:
                    gk_opt.first.click()
                    time.sleep(1)

            # Type name or code in new row input and select exact option
            search_query = name if name else code
            row_inps = page.locator('mat-form-field input:visible, input[placeholder*="genre" i]:visible')
            if row_inps.count() > 0:
                target_inp = row_inps.last
                target_inp.focus()
                target_inp.fill(search_query)
                time.sleep(1.5)

                # Search for exact name or parenthesized code
                opts = page.locator(f'mat-option:has-text("{name}"), [role="option"]:has-text("{name}")') if name else page.locator(f'mat-option:has-text("({code})"), [role="option"]:has-text("({code})")')
                if opts.count() == 0:
                    opts = page.locator(f'mat-option:has-text("({code})"), [role="option"]:has-text("({code})")')
                if opts.count() == 0:
                    opts = page.locator(f'mat-option:has-text("{code}"), [role="option"]:has-text("{code}")')

                if opts.count() > 0:
                    top_txt = opts.first.inner_text().strip().replace('\n', ' ')
                    opts.first.click()
                    print(f"  ✓ Added Genre: {top_txt}")
                    time.sleep(1)

        print("\n✨ Tab 2 (Genres) Populated! (Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill Google Books Tab 2 (Genres) & Pause for Review")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    fill_genres_tab(args.book, args.lang, port=args.port)
