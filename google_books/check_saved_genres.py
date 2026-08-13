"""
check_saved_genres.py
Inspects the active Google Books Genres page to verify if genres have been saved/added.
"""

import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_saved():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page URL: {page.url}")
        print(f"Active Page Title: {page.title()}\n")

        js_check = """
        () => {
            const warning = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.includes('No genres added'));
            const genresRows = Array.from(document.querySelectorAll('tr, mat-chip, .mat-chip, [class*="genre-item"], table tr, div.genre-row'));
            
            const rowTexts = genresRows.map(r => r.innerText.trim().replace(/\\n/g, ' ')).filter(t => t && !t.includes('Save') && !t.includes('industry-standard'));

            return {
                warning_visible: !!warning,
                genre_rows_count: rowTexts.length,
                added_genres: rowTexts
            };
        }
        """
        data = page.evaluate(js_check)
        print("=== Saved Genres Inspection Status ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    check_saved()
