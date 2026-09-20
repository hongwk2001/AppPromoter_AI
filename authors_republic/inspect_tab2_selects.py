import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_selects():
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

        selects = page.evaluate("""() => {
            const sels = Array.from(document.querySelectorAll('select'));
            return sels.map(s => ({
                id: s.id,
                name: s.name,
                class: s.className,
                optionsCount: s.options.length,
                firstOption: s.options[0] ? s.options[0].innerText.trim() : '',
                secondOption: s.options[1] ? s.options[1].innerText.trim() : ''
            }));
        }""")

        print(f"Select elements on page ({len(selects)}):")
        for s in selects:
            print(f"  <SELECT> id='{s['id']}' name='{s['name']}' count={s['optionsCount']} | 1st: '{s['firstOption']}' | 2nd: '{s['secondOption']}'")

if __name__ == "__main__":
    check_selects()
