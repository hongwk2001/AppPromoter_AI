import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_cover_js():
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

        script_info = page.evaluate("""() => {
            const scripts = Array.from(document.querySelectorAll('script')).map(s => s.innerText).filter(t => t.includes('cover') || t.includes('square-cover'));
            return scripts.slice(0, 5);
        }""")

        print(f"Scripts handling cover upload ({len(script_info)}):")
        for idx, s in enumerate(script_info, 1):
            print(f"--- Script {idx} ---")
            print(s[:1000])

if __name__ == "__main__":
    inspect_cover_js()
