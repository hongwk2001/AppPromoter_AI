import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_inputs():
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
            print("No page found")
            return

        inputs = page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('input[type="file"], input[type="hidden"], input[type="text"], button'));
            return els.map(i => ({
                tag: i.tagName.toLowerCase(),
                id: i.id,
                name: i.name,
                type: i.type,
                value: i.value ? i.value.substring(0, 50) : '',
                visible: !!(i.offsetWidth || i.offsetHeight || i.getClientRects().length)
            })).filter(x => x.id || x.name);
        }""")

        print(json.dumps(inputs, indent=2))

if __name__ == "__main__":
    inspect_inputs()
