"""
inspect_google_form.py
Scrapes all input, textarea, select, role="textbox", and label elements on the active Google Books page.
"""

import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_page():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page: {page.url} ({page.title()})\n")

        js = """
        () => {
            const els = Array.from(document.querySelectorAll('input, textarea, select, label, div[role="textbox"], div[contenteditable="true"]'));
            return els.map((el, i) => ({
                idx: i + 1,
                tag: el.tagName.toLowerCase(),
                type: el.type || el.getAttribute('type') || '',
                id: el.id || '',
                name: el.name || el.getAttribute('name') || '',
                aria_label: el.getAttribute('aria-label') || '',
                placeholder: el.getAttribute('placeholder') || '',
                value: el.value || el.innerText || '',
                visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)
            })).filter(e => e.visible);
        }
        """
        res = page.evaluate(js)
        print(f"Captured {len(res)} form elements:")
        print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    inspect_page()
