import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_tab2_errors():
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

        errors_info = page.evaluate("""() => {
            const errs = Array.from(document.querySelectorAll('.text-danger, .field-validation-error, .error, .invalid-feedback, span[id*="Error"]'));
            return errs.map(e => ({
                id: e.id,
                class: e.className,
                text: e.innerText.trim(),
                visible: !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length)
            })).filter(x => x.text.length > 0);
        }""")

        print(f"Validation Errors on current Tab ({len(errors_info)}):")
        for err in errors_info:
            print(f"  [{err['id']}] Class: '{err['class']}' | Text: '{err['text']}' | Visible: {err['visible']}")

if __name__ == "__main__":
    check_tab2_errors()
