import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_tabs():
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

        tabs = page.query_selector_all(".w-20, ul.nav-tabs li, nav a, .wizard-steps li")
        print(f"Total tabs found: {len(tabs)}")

        for idx, tab in enumerate(tabs, 1):
            tab_text = tab.inner_text().strip()
            print(f"\n==========================================")
            print(f"Attempting to inspect Tab [{idx}]: {tab_text}")
            print(f"==========================================")
            
            try:
                tab.click()
                time.sleep(1.5)
            except Exception as e:
                print(f"Could not click tab {tab_text}: {e}")

            # Inspect inputs currently visible
            visible_inputs = page.evaluate("""() => {
                const els = Array.from(document.querySelectorAll('input, select, textarea, button, label, div.dropzone, div[id*="upload"], div[class*="upload"]'));
                return els.map(el => {
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
                        text: el.innerText ? el.innerText.trim().replace(/\\s+/g, ' ') : '',
                        visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)
                    };
                }).filter(x => x.visible && ['input', 'select', 'textarea', 'button', 'div'].includes(x.tag));
            }""")

            print(f"Visible elements on Tab '{tab_text}' ({len(visible_inputs)} total):")
            for inp in visible_inputs:
                if inp['tag'] in ['input', 'select', 'textarea', 'button'] or 'upload' in inp['id'] or 'drop' in inp['class']:
                    print(f"  <{inp['tag'].upper()}> type='{inp['type']}' id='{inp['id']}' name='{inp['name']}' label='{inp['label']}' text='{inp['text'][:60]}'")

if __name__ == "__main__":
    inspect_tabs()
