import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_all_genres():
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

        genres = page.evaluate("""() => {
            const select = document.querySelector('#Genre1');
            if (!select) return [];
            return Array.from(select.options).map(o => ({ value: o.value, text: o.innerText.replace(/\\s+/g, ' ').trim() }));
        }""")

        print(f"Total Genre Options in #Genre1: {len(genres)}")
        for g in genres[1:30]:
            print(f"  Val: '{g['value']}' | Text: '{g['text']}'")

if __name__ == "__main__":
    inspect_all_genres()
