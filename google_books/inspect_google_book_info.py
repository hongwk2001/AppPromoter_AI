"""
inspect_google_book_info.py
Safely inspects and reports all fields across Google Books Partner Center Book Info tabs
WITHOUT clicking Save, Continue, or submitting any data.
"""

import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_safe():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page: {page.url} ({page.title()})\n")

        js = """
        () => {
            const result = {};
            
            // 1. Detect Active Sub-tab
            const activeTab = document.querySelector('.mat-mdc-tab-link.mdc-tab--active, .mat-tab-label-active');
            result.active_tab = activeTab ? activeTab.innerText.trim() : 'Unknown';

            // 2. Scrape all form fields on current view
            const formFields = Array.from(document.querySelectorAll('mat-form-field, .mat-form-field, div[class*="field"]'));
            const fieldList = [];

            formFields.forEach((c, idx) => {
                const labelEl = c.querySelector('label, .mat-form-field-label, [class*="label"], .mdc-floating-label');
                const inputEl = c.querySelector('input, textarea, select, mat-select, [contenteditable="true"]');
                const labelText = labelEl ? labelEl.innerText.trim().replace(/\\n/g, ' ') : '';
                const val = inputEl ? (inputEl.value || inputEl.innerText || '').trim() : '';
                const placeholder = inputEl ? (inputEl.getAttribute('placeholder') || '') : '';
                
                if (labelText || inputEl) {
                    fieldList.push({
                        idx: idx + 1,
                        label: labelText,
                        tag: inputEl ? inputEl.tagName.toLowerCase() : '',
                        type: inputEl ? (inputEl.type || inputEl.getAttribute('type') || '') : '',
                        id: inputEl ? inputEl.id : '',
                        value: val,
                        placeholder: placeholder
                    });
                }
            });

            result.fields = fieldList;
            return result;
        }
        """
        data = page.evaluate(js)
        print(f"=== Active Sub-tab: {data['active_tab']} ===")
        print(f"Captured {len(data['fields'])} form fields on current tab:\n")
        print(json.dumps(data["fields"], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    inspect_safe()
