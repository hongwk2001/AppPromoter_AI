"""
dump_page_text.py
Captures a screenshot of the active Google Books Genres page and dumps all visible text elements.
"""

import os
import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = r"C:\Users\hongw\.gemini\antigravity\brain\fcdef50b-7379-4582-be2a-e64f8c42643d"

def dump_page():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page: {page.url}\n")

        # 1. Take screenshot
        ss_path = os.path.join(ARTIFACTS_DIR, "google_books_genres_tab.png")
        page.screenshot(path=ss_path, full_page=True)
        print(f"✅ Saved screenshot to: {ss_path}")

        # 2. Extract visible text
        js = """
        () => {
            const container = document.querySelector('mat-sidenav-content, main, body');
            return container ? container.innerText : document.body.innerText;
        }
        """
        text = page.evaluate(js)
        print("\n=== Active Page Visible Text ===")
        print(text[:1500])

if __name__ == "__main__":
    dump_page()
