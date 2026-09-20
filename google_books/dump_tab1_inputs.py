import os
import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def dump_inputs(port=9222):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "info/" in pg.url]
        if not pages:
            pages = browser.contexts[0].pages
        page = pages[0]
        print(f"Connected to page: {page.url} ({page.title()})\n")

        form_fields = page.evaluate("""
        () => {
            const fields = Array.from(document.querySelectorAll('mat-form-field, .form-field'));
            return fields.map((f, idx) => {
                const label = f.querySelector('label, mat-label, .mat-form-field-label');
                const inp = f.querySelector('input, textarea, mat-select');
                return {
                    idx: idx,
                    label: label ? label.innerText.trim() : '',
                    innerText: f.innerText.replace(/\\n/g, ' | ').substring(0, 150),
                    inpTag: inp ? inp.tagName : '',
                    inpId: inp ? inp.id : '',
                    inpPlaceholder: inp ? inp.placeholder : '',
                    inpValue: inp ? inp.value || inp.innerText : ''
                };
            });
        }
        """)
        print(json.dumps(form_fields, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    dump_inputs()
