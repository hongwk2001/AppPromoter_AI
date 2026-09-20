import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_sample():
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

        state = page.evaluate("""() => {
            const containers = Array.from(document.querySelectorAll('.upload-file-col, .audio-file-wrapper, div[class*="upload"]'));
            const sampleCol = containers.find(c => c.innerText.includes('Sample Track'));
            return {
                sample_col_text: sampleCol ? sampleCol.innerText.replace(/\\n+/g, ' ').trim() : 'Not Found'
            };
        }""")

        print(f"Sample Track Section State: {state['sample_col_text']}")

if __name__ == "__main__":
    check_sample()
