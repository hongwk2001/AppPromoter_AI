"""
inspect_genre_button_state.py
Inspects exact HTML structure, disabled status, and attributes of the 'Add a genre' button.
"""

import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_button():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page: {page.url}\n")

        js_inspect = """
        () => {
            const btns = Array.from(document.querySelectorAll('button, [role="button"]'));
            const matches = btns.filter(b => b.innerText && (b.innerText.includes('Add') || b.innerText.includes('genre')));
            return matches.map((b, i) => ({
                idx: i + 1,
                tag: b.tagName.toLowerCase(),
                id: b.id || '',
                class: b.className || '',
                disabled: b.disabled || b.getAttribute('disabled') || false,
                aria_disabled: b.getAttribute('aria-disabled') || 'false',
                outerHTML: b.outerHTML.substring(0, 200)
            }));
        }
        """
        data = page.evaluate(js_inspect)
        print("=== Add Genre Buttons Captured ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    inspect_button()
