import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_error():
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
            const errs = Array.from(document.querySelectorAll('.field-validation-error, .text-danger, .alert-danger, .toast-body, .qq-upload-failed-text, .qq-upload-status-text')).map(e => e.innerText.trim()).filter(Boolean);
            const containers = Array.from(document.querySelectorAll('.form-group, .mb-3, tr, td, div')).filter(d => d.innerText && d.innerText.includes('Closing')).map(d => d.innerText.trim().replace(/\\s+/g, ' '));
            return {
                errors: errs,
                closingContainer: containers
            };
        }""")

        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    inspect_error()
