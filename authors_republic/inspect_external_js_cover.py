import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def find_cover_js():
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

        funcs = page.evaluate("""() => {
            const results = [];
            // Check window functions or jQuery handlers
            if (window.$ && $.data) {
                const el = $('#square-cover-file')[0];
                if (el) {
                    const events = $._data(el, 'events');
                    if (events) {
                        results.push(Object.keys(events));
                    }
                }
                const label = $('.cover-select')[0];
                if (label) {
                    const events = $._data(label, 'events');
                    if (events) {
                        results.push(Object.keys(events));
                    }
                }
            }
            return results;
        }""")

        print(f"jQuery event handlers attached: {funcs}")

if __name__ == "__main__":
    find_cover_js()
