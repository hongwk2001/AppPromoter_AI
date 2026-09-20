import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_cover_html():
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

        html = page.evaluate("""() => {
            const container = document.querySelector('#audio-covers-wrapper');
            return container ? container.outerHTML : 'Not found';
        }""")

        print("=== AUDIO COVERS WRAPPER HTML ===")
        print(html[:2000])

if __name__ == "__main__":
    inspect_cover_html()
