"""
google_audio_1b_fill_genres.py
Populates the Genres sub-tab for Google Books Audiobook Partner Center entries over CDP port 9222.
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
    "blue_castle": [
        {"code": "102", "name": "영미소설"},
        {"code": "106", "name": "동서양고전"},
        {"code": "100", "name": "소설"}
    ],
    "beowulf": [
        {"code": "106", "name": "동서양고전"},
        {"code": "102", "name": "영미소설"},
        {"code": "100", "name": "소설"}
    ],
    "dracula": [
        {"code": "106", "name": "동서양고전"},
        {"code": "102", "name": "영미소설"},
        {"code": "100", "name": "소설"}
    ]
}

BISAC_PRESETS = {
    "blue_castle": [
        "FICTION / Classics",
        "FICTION / Romance / General",
        "FICTION / Women's Fiction"
    ],
    "beowulf": [
        "FICTION / Classics",
        "FICTION / Action & Adventure"
    ],
    "dracula": [
        "FICTION / Classics",
        "FOREIGN LANGUAGE STUDY / Korean",
        "FICTION / Horror"
    ]
}

def load_audio_metadata(book_name, lang="ko"):
    meta_path = os.path.join(NOTES_DIR, f"google_audio_metadata_{book_name}_{lang}.json")
    if not os.path.exists(meta_path):
        from google_audio_0_prepare_metadata import prepare_audio_metadata
        return prepare_audio_metadata(book_name, lang)
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def fill_audio_genres(book_name, lang="ko", port=9222):
    data = load_audio_metadata(book_name, lang)
    if not data:
        print("Error: Could not load Audiobook metadata.")
        return

    if lang == "ko":
        gkss = GKSS_PRESETS.get(book_name, [{"code": "106", "name": "동서양고전"}, {"code": "102", "name": "영미소설"}])
        genres = [item["name"] if isinstance(item, dict) else item for item in gkss]
    else:
        genres = BISAC_PRESETS.get(book_name, ["FICTION / Classics", "FICTION / Action & Adventure"])

    print(f"\n📋 Filling Google Books Audiobook Genres for: {book_name} ({lang.upper()})")
    print(f"  Target Genres: {genres}\n")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page: {page.url} ({page.title()})")

        # Dismiss any open Angular Material overlays (backdrops, dropdowns)
        page.keyboard.press("Escape")
        time.sleep(0.5)

        # 1. Switch to Genres sub-tab if needed
        if "info/genres" not in page.url:
            genre_tab = page.locator('a[href*="info/genres"], a:has-text("Genres"), span:has-text("Genres"), div[role="tab"]:has-text("Genres")')
            if genre_tab.count() > 0:
                print("➡️ Switching to Genres tab...")
                genre_tab.first.click(force=True)
                time.sleep(1.5)

        # 2. Add each genre
        for genre_str in genres:
            add_btn = page.locator('button:has-text("Add a genre"), [role="button"]:has-text("Add a genre")')
            if add_btn.count() > 0:
                add_btn.first.click()
                time.sleep(1)

            # Locate the latest input field
            inputs = page.locator('input[placeholder*="Genre"], input[aria-label*="Genre"], mat-select, input')
            if inputs.count() > 0:
                inp = inputs.last
                inp.click()
                inp.fill(genre_str)
                time.sleep(1)
                
                # Press Enter or ArrowDown + Enter to select option
                page.keyboard.press("ArrowDown")
                time.sleep(0.5)
                page.keyboard.press("Enter")
                print(f"  ✓ Added Genre: {genre_str}")
                time.sleep(1)

        print("\n✨ Audiobook Genres Autofill Finished! (Form populated — Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill Google Play Books Audiobook Genres")
    parser.add_argument("--book", type=str, required=True, help="Book key or folder path")
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    args = parser.parse_args()

    fill_audio_genres(args.book, args.lang)
