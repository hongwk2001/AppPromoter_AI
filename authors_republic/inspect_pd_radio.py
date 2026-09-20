import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_pd():
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

        pd_html = page.evaluate("""() => {
            const label = Array.from(document.querySelectorAll('label, div')).find(e => e.innerText.includes('Public Domain?'));
            if (!label) return 'Not found';
            const parent = label.closest('.row') || label.closest('div');
            return parent ? parent.innerHTML : 'No parent';
        }""")

        print("=== PUBLIC DOMAIN HTML ===")
        print(pd_html)

if __name__ == "__main__":
    inspect_pd()
