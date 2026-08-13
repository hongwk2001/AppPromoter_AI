"""
inspect_all_tabs.py
Inspects all 5 sub-tabs under Book Info in Google Books Partner Center.
"""

import sys
import time
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_tabs():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page: {page.url} ({page.title()})\n")

        tab_names = ["About the book", "Genres", "Contributors", "Series", "Settings"]
        
        for name in tab_names:
            print(f"=== Sub-tab: {name} ===")
            tab_loc = page.locator(f'a:has-text("{name}"), span:has-text("{name}")')
            if tab_loc.count() > 0:
                try:
                    tab_loc.first.click()
                    time.sleep(1.5)
                except Exception as e:
                    print(f"  Could not click tab {name}: {e}")

            js = """
            () => {
                const inputs = Array.from(document.querySelectorAll('input, textarea, select, mat-select, [contenteditable="true"], button'));
                return inputs.map(inp => {
                    const parent = inp.closest('mat-form-field') || inp.parentElement;
                    const lbl = parent ? parent.querySelector('label, [class*="label"]') : null;
                    return {
                        id: inp.id || '',
                        tag: inp.tagName.toLowerCase(),
                        type: inp.type || '',
                        label: lbl ? lbl.innerText.trim().replace(/\\n/g, ' ') : '',
                        value: (inp.value || inp.innerText || '').substring(0, 50).replace(/\\n/g, ' '),
                        placeholder: inp.getAttribute('placeholder') || ''
                    };
                }).filter(e => e.label || e.id || e.placeholder || e.tag === 'mat-select');
            }
            """
            fields = page.evaluate(js)
            print(json.dumps(fields[:15], indent=2, ensure_ascii=False))
            print("\n")

if __name__ == "__main__":
    inspect_tabs()
