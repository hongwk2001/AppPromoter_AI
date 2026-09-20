import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_pd():
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

        pd_info = page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('input, select, textarea, label, div')).filter(el => {
                const txt = (el.innerText || el.value || '').toLowerCase();
                const id = (el.id || '').toLowerCase();
                const name = (el.name || '').toLowerCase();
                return txt.includes('public domain') || id.includes('public') || name.includes('public') || id.includes('domain') || name.includes('domain');
            });

            return els.map(e => ({
                tag: e.tagName.toLowerCase(),
                type: e.type || '',
                id: e.id || '',
                name: e.name || '',
                text: e.innerText ? e.innerText.substring(0, 100).replace(/\\n+/g, ' ') : '',
                checked: e.checked || false,
                value: e.value || ''
            }));
        }""")

        print(f"Public Domain fields found ({len(pd_info)}):")
        for item in pd_info:
            print(f" <{item['tag'].upper()}> type='{item['type']}' id='{item['id']}' name='{item['name']}' checked={item['checked']} value='{item['value']}' text='{item['text']}'")

if __name__ == "__main__":
    check_pd()
