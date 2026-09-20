import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_tab2_pd():
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

        print(f"Current page URL: {page.url}")

        # Click Tab 2 (Metadata)
        tabs = page.query_selector_all(".w-20, ul.nav-tabs li, nav a")
        if len(tabs) >= 2:
            print("Clicking Tab 2 (Metadata)...")
            tabs[1].click()
            time.sleep(2.0)

        # Inspect all radios and labels on Tab 2
        tab2_radios = page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('input, select, textarea, label, fieldset, div')).filter(e => {
                const text = (e.innerText || '').toLowerCase();
                return text.includes('public domain') || text.includes('copyright') || text.includes('owner') || text.includes('rights');
            });

            return els.map(e => ({
                tag: e.tagName.toLowerCase(),
                id: e.id || '',
                name: e.name || '',
                type: e.type || '',
                text: e.innerText ? e.innerText.substring(0, 150).replace(/\\n+/g, ' ') : ''
            }));
        }""")

        print(f"\nTab 2 Copyright / Public Domain elements ({len(tab2_radios)}):")
        for item in tab2_radios[:15]:
            print(f" <{item['tag'].upper()}> id='{item['id']}' name='{item['name']}' type='{item['type']}' text='{item['text']}'")

if __name__ == "__main__":
    check_tab2_pd()
