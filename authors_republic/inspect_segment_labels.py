import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_segments():
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

        res = page.evaluate("""() => {
            const inputs = Array.from(document.querySelectorAll('input.chunkUploader, input[data-segment-id]'));
            return inputs.map(el => {
                const segId = el.getAttribute('data-segment-id');
                const container = el.closest('.form-group, .mb-3, div, td, tr') || el.parentElement;
                const text = container ? container.innerText.trim().replace(/\\s+/g, ' ') : '';
                return {
                    segmentId: segId,
                    id: el.id,
                    containerText: text.substring(0, 150)
                };
            });
        }""")

        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    inspect_segments()
