import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_state():
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

        print(f"Current URL: {page.url}")
        info = page.evaluate("""() => {
            const active = document.querySelector('.w-20.active, .nav-tabs .active, .wizard-steps .active, [aria-selected="true"]');
            const submitBtn = document.querySelector('#SubmitBtn, button[type="submit"], input[type="submit"]');
            return {
                activeTab: active ? active.innerText.trim() : 'Unknown',
                submitBtnText: submitBtn ? (submitBtn.innerText || submitBtn.value) : 'None'
            };
        }""")
        print(f"Active Tab: {info['activeTab']}")
        print(f"Submit Button: {info['submitBtnText']}")

if __name__ == "__main__":
    check_state()
