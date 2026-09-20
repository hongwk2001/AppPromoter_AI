import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_tabs():
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

        # Check tabs text and clickability
        tabs = page.query_selector_all(".w-20, ul.nav-tabs li, nav a, .wizard-steps li")
        print(f"Found {len(tabs)} tabs:")
        for idx, tab in enumerate(tabs, 1):
            text = tab.inner_text().strip()
            is_clickable = tab.is_enabled()
            print(f" Tab {idx}: '{text}' | Enabled: {is_clickable}")

        # Let's inspect all html forms and step divs in page DOM
        steps_info = page.evaluate("""() => {
            const divs = Array.from(document.querySelectorAll('div, section, form')).filter(d => d.id || d.className);
            return divs.map(d => ({
                id: d.id,
                class: d.className,
                visible: !!(d.offsetWidth || d.offsetHeight || d.getClientRects().length),
                text_head: d.innerText ? d.innerText.substring(0, 100).replace(/\\n+/g, ' ') : ''
            })).filter(d => d.id.includes('step') || d.id.includes('Tab') || d.id.includes('Meta') || d.id.includes('Project') || d.class.includes('step') || d.class.includes('tab'));
        }""")

        print("\nStep / Tab Containers in DOM:")
        for s in steps_info:
            print(f" ID: '{s['id']}' | Class: '{s['class']}' | Visible: {s['visible']} | Text: {s['text_head']}")

if __name__ == "__main__":
    check_tabs()
