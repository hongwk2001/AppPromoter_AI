import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_live_status():
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

        print(f"Current page URL: {page.url}")
        print(f"Current page Title: {page.title()}")

        # Check values in inputs
        title_val = page.input_value("#Project_ProjectName") if page.query_selector("#Project_ProjectName") else "N/A"
        subtitle_val = page.input_value("#Project_SubTitle") if page.query_selector("#Project_SubTitle") else "N/A"
        print(f"Title Field Value: {title_val}")
        print(f"Subtitle Field Value: {subtitle_val}")

        # Check active tab
        active_tab = page.evaluate("""() => {
            const active = document.querySelector('.w-20.active, .nav-tabs .active, .wizard-steps .active, [aria-selected="true"]');
            return active ? active.innerText.trim() : 'Unknown';
        }""")
        print(f"Active Tab: {active_tab}")

if __name__ == "__main__":
    check_live_status()
