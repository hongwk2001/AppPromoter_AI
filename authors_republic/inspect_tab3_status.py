import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_tab3():
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
            const errs = Array.from(document.querySelectorAll('.field-validation-error, .text-danger, .alert-danger, .validation-summary-errors')).map(el => el.innerText.trim()).filter(Boolean);
            const btn = document.querySelector('#AgreementBtn');
            const btnVisible = btn ? !!(btn.offsetWidth || btn.offsetHeight) : false;
            const btnDisabled = btn ? btn.disabled : false;
            
            const coverInput = document.querySelector('#square-cover-file');
            const coverImg = document.querySelector('#square-cover-img, img[src*="cover"]');

            return {
                errors: errs,
                btnVisible: btnVisible,
                btnDisabled: btnDisabled,
                coverImgSrc: coverImg ? coverImg.src : 'No cover img'
            };
        }""")

        print("Tab 3 Form Analysis:")
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    inspect_tab3()
