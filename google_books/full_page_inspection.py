"""
full_page_inspection.py
Exhaustively inspects every form input on the active Google Books page,
finding its surrounding Angular Material label text, ID, tag, and current value.
"""

import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_full():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page URL: {page.url}")
        print(f"Active Page Title: {page.title()}\n")

        js = """
        () => {
            const inputs = Array.from(document.querySelectorAll('input, textarea, select, mat-select, [contenteditable="true"]'));
            const fieldList = [];

            inputs.forEach((inp, idx) => {
                const tag = inp.tagName.toLowerCase();
                const id = inp.id || '';
                const type = inp.type || inp.getAttribute('type') || '';
                const placeholder = inp.getAttribute('placeholder') || '';
                const val = (inp.value || inp.innerText || '').trim();

                // Find associated label text by looking up parent hierarchy
                let labelText = '';
                let p = inp;
                for (let level = 0; level < 6; level++) {
                    if (p && p.parentElement) {
                        p = p.parentElement;
                        const labelEl = p.querySelector('label, mat-label, .mat-form-field-label, [class*="label"], [class*="title"]');
                        if (labelEl && labelEl.innerText.trim() && !labelEl.innerText.includes('Save')) {
                            labelText = labelEl.innerText.trim().replace(/\\n/g, ' ');
                            break;
                        }
                    }
                }

                fieldList.push({
                    field_number: idx + 1,
                    label_name: labelText || placeholder || '(No label)',
                    id: id,
                    tag: tag,
                    type: type,
                    current_value: val.replace(/\\n/g, ' ').substring(0, 80),
                    placeholder: placeholder
                });
            });

            return {
                page_url: window.location.href,
                page_title: document.title,
                total_fields: fieldList.length,
                fields: fieldList
            };
        }
        """
        scraped_data = page.evaluate(js)
        
        # Save to JSON file as well
        output_file = r"C:\git_repo\AppPromoter_AI\notes\google_books_active_page_inspection.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)

        print(json.dumps(scraped_data, indent=2, ensure_ascii=False))
        print(f"\nSaved inspection JSON to: {output_file}")

if __name__ == "__main__":
    inspect_full()
