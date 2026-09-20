import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_tabs_details():
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

        print(f"URL: {page.url}")

        # Extract all tabs and their containers/steps
        tabs_details = page.evaluate("""() => {
            const tabsData = [];
            const tabLinks = Array.from(document.querySelectorAll('.w-20, ul.nav-tabs li, nav a, .wizard-steps li'));
            
            // Get all sections / form containers
            const forms = Array.from(document.querySelectorAll('form, fieldset, .tab-pane, section, div[id*="step"], div[id*="tab"]'));

            const inputs = Array.from(document.querySelectorAll('input, select, textarea, button, label')).map(el => {
                let label = '';
                if (el.labels && el.labels[0]) label = el.labels[0].innerText.trim();
                else if (el.closest('label')) label = el.closest('label').innerText.trim();
                else if (el.previousElementSibling && el.previousElementSibling.tagName === 'LABEL') label = el.previousElementSibling.innerText.trim();
                
                return {
                    tag: el.tagName.toLowerCase(),
                    type: el.type || '',
                    id: el.id || '',
                    name: el.name || '',
                    class: el.className || '',
                    label: label,
                    placeholder: el.placeholder || '',
                    text: el.innerText ? el.innerText.trim() : '',
                    value: el.value || '',
                    visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)
                };
            });

            return {
                tabs: tabLinks.map(t => t.innerText.trim()),
                inputs: inputs,
                forms: forms.map(f => ({ id: f.id, class: f.className, text: f.innerText.substring(0, 300) }))
            };
        }""")

        print("\n=== TAB NAMES ===")
        for t in tabs_details['tabs']:
            if t:
                print(f" - {t}")

        print("\n=== VISIBLE INPUTS & BUTTONS ===")
        for inp in tabs_details['inputs']:
            if inp['visible'] and inp['tag'] in ['input', 'select', 'textarea', 'button']:
                print(f"[{inp['tag'].upper()}] type='{inp['type']}' id='{inp['id']}' name='{inp['name']}' label='{inp['label']}' text='{inp['text']}'")

if __name__ == "__main__":
    inspect_tabs_details()
