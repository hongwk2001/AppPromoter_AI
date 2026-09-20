import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_all_tabs():
    cdp_url = "http://127.0.0.1:9222"
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0]
        page = None
        for page_obj in context.pages:
            if "authorsrepublic.com" in page_obj.url:
                page = page_obj
                break
        if not page:
            page = context.pages[0]

        print(f"Connected to page: {page.url} - {page.title()}")

        tabs_data = {}
        
        # Get tab element text/selectors
        tabs_elements = page.query_selector_all("ul.nav-tabs li, nav a, .w-20, div.text-center")
        print(f"Found {len(tabs_elements)} tab candidate elements")

        # Detailed inspection function
        tab_names = ["Get Started", "Metadata", "Audio & Cover Art", "Agreement"]

        # Evaluate entire page structure via JS
        structure = page.evaluate("""() => {
            function getFields(container) {
                const elements = Array.from(container.querySelectorAll('input, select, textarea, button, label, .dropzone, form, a.btn'));
                return elements.map(el => {
                    const label = el.labels && el.labels[0] ? el.labels[0].innerText.trim() : 
                                 (el.closest('label') ? el.closest('label').innerText.trim() : 
                                 (el.previousElementSibling && el.previousElementSibling.tagName === 'LABEL' ? el.previousElementSibling.innerText.trim() : ''));
                    return {
                        tag: el.tagName.toLowerCase(),
                        type: el.type || '',
                        id: el.id || '',
                        name: el.name || '',
                        class: el.className || '',
                        label: label,
                        placeholder: el.placeholder || '',
                        text: el.innerText ? el.innerText.trim().replace(/\\s+/g, ' ') : '',
                        visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)
                    };
                });
            }

            const tabs = Array.from(document.querySelectorAll('.w-20, ul.nav-tabs li, .nav-item, nav a')).map(t => ({
                text: t.innerText.trim(),
                id: t.id,
                class: t.className
            })).filter(t => t.text.length > 0);

            return {
                tabs: tabs,
                all_fields: getFields(document.body),
                page_html_snippet: document.body.innerHTML.substring(0, 3000)
            };
        }""")

        with open("ar_full_structure.json", "w", encoding="utf-8") as f:
            json.dump(structure, f, ensure_ascii=False, indent=2)
        print("Saved full page structure to ar_full_structure.json")

if __name__ == "__main__":
    inspect_all_tabs()
