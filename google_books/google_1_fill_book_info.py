"""
google_1_fill_book_info.py
Populates Tab 1 (About the book) fields (Title, Subtitle, Description, Language, Publisher, Page Count)
on active Google Books Partner Center tab over CDP port 9222.
STOPS immediately after filling for user review — does NOT click Save, Next, or submit.
"""

import os
import sys
import json
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

        js_fill_tab1 = """
        (data) => {
            const filled = [];

            function setVal(input, val) {
                if (!input || val === undefined || val === null) return false;
                input.focus();
                input.value = val;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                input.dispatchEvent(new Event('blur', { bubbles: true }));
                return true;
            }

            function findInputByContext(labelTxt) {
                const inputs = Array.from(document.querySelectorAll('input, textarea'));
                for (const i of inputs) {
                    let p = i;
                    let ctx = '';
                    for (let level = 0; level < 6; level++) {
                        if (p.parentElement) {
                            p = p.parentElement;
                            ctx += ' ' + p.innerText;
                        }
                    }
                    if (ctx.toLowerCase().includes(labelTxt.toLowerCase())) {
                        return i;
                    }
                }
                return null;
            }

            // 1. Title (Must be set first to enable Add a Subtitle button)
            const inputs = Array.from(document.querySelectorAll('input'));
            const titleInp = inputs.find(i => {
                const p = i.closest('mat-form-field') || i.parentElement;
                const txt = (p ? p.innerText : '').toLowerCase();
                return txt.includes('title') && !txt.includes('subtitle');
            }) || inputs[0];

            if (setVal(titleInp, data.title)) filled.push('Title');

            // 2. Subtitle (Enabled after title is entered)
            if (data.subtitle) {
                let subInp = findInputByContext('subtitle') || document.querySelector('input[placeholder*="Subtitle" i]');
                if (!subInp) {
                    const subBtn = Array.from(document.querySelectorAll('button, [role="button"], a, span')).find(b => b.innerText && b.innerText.toLowerCase().includes('subtitle'));
                    if (subBtn && !subBtn.disabled && subBtn.getAttribute('aria-disabled') !== 'true') {
                        subBtn.click();
                    }
                    subInp = findInputByContext('subtitle') || document.querySelector('input[placeholder*="Subtitle" i]');
                }
                if (setVal(subInp, data.subtitle)) filled.push('Subtitle');
            }

            // 3. Description (Quill Editor)
            const descDiv = document.querySelector('div.ql-editor, div[contenteditable="true"], div[role="textbox"]');
            if (descDiv) {
                descDiv.focus();
                descDiv.innerHTML = data.desc_html || ('<p>' + (data.description_text || '') + '</p>');
                descDiv.dispatchEvent(new Event('input', { bubbles: true }));
                descDiv.dispatchEvent(new Event('change', { bubbles: true }));
                descDiv.dispatchEvent(new Event('blur', { bubbles: true }));
                filled.push('Description');
            }

            // 4. Language
            const langInp = findInputByContext('language') || document.querySelector('#mat-input-3');
            if (setVal(langInp, data.language || 'Korean')) filled.push('Language');

            // 5. Publisher
            if (data.publisher) {
                const pubInp = findInputByContext('publisher') || document.querySelector('input[placeholder="Name"]');
                if (setVal(pubInp, data.publisher)) filled.push('Publisher');
            }

            // 6. Page Count
            if (data.page_count) {
                const pageInp = findInputByContext('page count');
                if (setVal(pageInp, data.page_count)) filled.push('Page count');
            }

            if (document.activeElement) {
                document.activeElement.blur();
            }

            return filled;
        }
        """

        payload = {
            "title": tab1.get("title", ""),
            "subtitle": tab1.get("subtitle", ""),
            "publisher": tab1.get("publisher", "TKPROF LLC"),
            "language": tab1.get("language", "Korean"),
            "page_count": tab1.get("page_count", "411"),
            "description_text": desc_raw,
            "desc_html": desc_html
        }

        filled_fields = page.evaluate(js_fill_tab1, payload)
        if filled_fields:
            print(f"  ✓ Populated Tab 1 fields cleanly: {', '.join(filled_fields)}")

        print("\n✨ Tab 1 (About the book) Populated! (Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill Google Books Tab 1 (About the book) & Pause for Review")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    fill_tab1_about_the_book(args.book, args.lang, port=args.port)
