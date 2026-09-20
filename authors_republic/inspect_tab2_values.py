import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_tab2_values():
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

        vals = page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('input, select, textarea'));
            return els.map(el => {
                let label = '';
                if (el.labels && el.labels[0]) label = el.labels[0].innerText.trim();
                else if (el.closest('label')) label = el.closest('label').innerText.trim();
                else if (el.previousElementSibling && el.previousElementSibling.tagName === 'LABEL') label = el.previousElementSibling.innerText.trim();

                return {
                    tag: el.tagName.toLowerCase(),
                    type: el.type || '',
                    id: el.id,
                    name: el.name,
                    label: label,
                    value: el.value ? el.value.substring(0, 50) : '',
                    checked: el.type === 'radio' || el.type === 'checkbox' ? el.checked : false,
                    visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)
                };
            }).filter(x => x.visible);
        }""")

        print("\n=== TAB 2 FIELD VALUES ===")
        for v in vals:
            print(f"[{v['tag'].upper()}] id='{v['id']}' label='{v['label']}' value='{v['value']}' checked={v['checked']}")

if __name__ == "__main__":
    check_tab2_values()
