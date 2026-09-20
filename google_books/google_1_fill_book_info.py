"""
google_1_fill_book_info.py
Populates Tab 1 (About the book) fields (Title, Subtitle, Description, Language, Publisher, Page Count)
on active Google Books Partner Center tab over CDP port 9222.
STOPS immediately after filling for user review — does NOT click Save, Next, or submit.
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

def fill_tab1_about_the_book(book_name, lang="ko", port=9222):
    data = load_google_metadata(book_name, lang)
    if not data:
        print("Error: Could not load Google Books metadata.")
        return

    tab1 = data.get("tab1_about_the_book", data.get("book_info", {}))
    print(f"\n📋 Filling Google Books Tab 1 (About the book) for: {tab1['title']} ({lang.upper()})")
    print(f"  Publisher:  {tab1.get('publisher', 'TKPROF LLC')}")
    print(f"  Language:   {tab1.get('language', 'Korean')}")
    print(f"  Page count: {tab1.get('page_count', '411')}\n")

    # Format description into clean single-spaced HTML paragraphs
    desc_raw = tab1.get("description_text", "")
    paragraphs = [p.strip().replace("\n", "<br>") for p in desc_raw.split("\n\n") if p.strip()]
    desc_html = "".join([f"<p>{p}</p>" for p in paragraphs])

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
        print(f"Active Tab: {page.url} ({page.title()})")

        # 1. Fill Title (mat-input-1 or formfield with Title label)
        title_val = tab1.get("title", "")
        title_inp = page.locator('#mat-input-1, mat-form-field:has-text("Title") input').first
        if title_inp.count() > 0:
            title_inp.click()
            title_inp.fill(title_val)
            print(f"  ✓ Title set to: {title_val}")

        # 2. Fill Subtitle
        sub_val = tab1.get("subtitle", "")
        if sub_val:
            sub_inp = page.locator('#mat-input-10, input[placeholder*="Subtitle" i], mat-form-field:has-text("Subtitle") input').first
            if sub_inp.count() == 0 or not sub_inp.is_visible():
                add_sub_btn = page.locator('button:has-text("Subtitle"), [role="button"]:has-text("Subtitle")')
                if add_sub_btn.count() > 0:
                    add_sub_btn.first.click()
                    time.sleep(1)
            sub_inp = page.locator('#mat-input-10, input[placeholder*="Subtitle" i], mat-form-field:has-text("Subtitle") input').first
            if sub_inp.count() > 0:
                sub_inp.click()
                sub_inp.fill(sub_val)
                print(f"  ✓ Subtitle set to: {sub_val}")

        # 3. Fill Description (Quill Editor)
        desc_div = page.locator('div.ql-editor, div[contenteditable="true"], div[role="textbox"]').first
        if desc_div.count() > 0:
            desc_div.click()
            page.evaluate("(html) => { const el = document.querySelector('div.ql-editor, div[contenteditable=\"true\"], div[role=\"textbox\"]'); if(el) { el.innerHTML = html; el.dispatchEvent(new Event('input', {bubbles:true})); } }", desc_html)
            print("  ✓ Description formatted & set")

        # 4. Fill Language (mat-input-3)
        lang_val = "Korean" if lang == "ko" else "English"
        lang_inp = page.locator('#mat-input-3, mat-form-field:has-text("Language") input').first
        if lang_inp.count() > 0:
            lang_inp.click()
            lang_inp.fill(lang_val)
            time.sleep(1)
            opt = page.locator(f'mat-option:has-text("{lang_val}"), [role="option"]:has-text("{lang_val}")').first
            if opt.count() > 0:
                opt.click()
                print(f"  ✓ Language selected from dropdown: {lang_val}")

        # 5. Fill Publisher (mat-input-4)
        pub_val = tab1.get("publisher", "TKPROF LLC")
        pub_inp = page.locator('#mat-input-4, input[placeholder="Name"]').first
        if pub_inp.count() > 0:
            pub_inp.click()
            pub_inp.fill(pub_val)
            print(f"  ✓ Publisher set to: {pub_val}")

        # 6. Fill Page Count (mat-input-7)
        page_val = tab1.get("page_count", "320")
        page_inp = page.locator('#mat-input-7, mat-form-field:has-text("integer") input').first
        if page_inp.count() > 0:
            page_inp.click()
            page_inp.fill(page_val)
            print(f"  ✓ Page count set to: {page_val}")

        print("\n✨ Tab 1 (About the book) Populated! (Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill Google Books Tab 1 (About the book) & Pause for Review")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    fill_tab1_about_the_book(args.book, args.lang, port=args.port)
