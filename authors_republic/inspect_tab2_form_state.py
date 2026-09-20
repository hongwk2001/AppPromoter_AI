import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_tab2():
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

        tab2_info = page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('input, select, textarea, button, label'));
            return els.map(el => {
                let label = '';
                if (el.labels && el.labels[0]) label = el.labels[0].innerText.trim();
                else if (el.closest('label')) label = el.closest('label').innerText.trim();
                else if (el.previousElementSibling && el.previousElementSibling.tagName === 'LABEL') label = el.previousElementSibling.innerText.trim();

                let options = [];
                if (el.tagName === 'SELECT') {
                    options = Array.from(el.options).map(o => ({ value: o.value, text: o.innerText.trim() }));
                }

                return {
                    tag: el.tagName.toLowerCase(),
                    type: el.type || '',
                    id: el.id || '',
                    name: el.name || '',
                    class: el.className || '',
                    label: label,
                    placeholder: el.placeholder || '',
                    text: el.innerText ? el.innerText.trim().replace(/\\s+/g, ' ') : '',
                    options_sample: options.slice(0, 10),
                    visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)
                };
            }).filter(x => x.visible);
        }""")

        print(f"\n=== TAB 2 (METADATA) VISIBLE CONTROLS ({len(tab2_info)}) ===")
        for item in tab2_info:
            print(f"<{item['tag'].upper()}> type='{item['type']}' id='{item['id']}' name='{item['name']}' label='{item['label']}' text='{item['text'][:40]}'")
            if item['options_sample']:
                print(f"   Options ({len(item['options_sample'])}): {[o['text'] for o in item['options_sample']]}")

if __name__ == "__main__":
    inspect_tab2()
