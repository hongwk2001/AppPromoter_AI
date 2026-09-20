import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def find_failing_keywords():
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

        test_cases = [
            "Richest Man in Babylon;personal finance;George S. Clason;money;investing;audiobook;wealth;classics",
            "Richest Man in Babylon; personal finance; George S. Clason; money; investing; audiobook; wealth; classics",
            "Richest Man in Babylon; personal finance; George Clason; money; investing; audiobook; wealth",
            "Richest Man in Babylon; personal finance; money; investing; audiobook; wealth",
            "personal finance; money; investing; wealth; classics; babylon"
        ]

        for s in test_cases:
            page.fill("#ProjectMeta_Keywords", s)
            # Trigger custom input event if any custom JS listener is bound
            page.evaluate("""(val) => {
                const el = document.querySelector('#ProjectMeta_Keywords');
                el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true }));
            }""", s)
            
            # Check form error element
            res = page.evaluate("""() => {
                const span = document.querySelector('[data-valmsg-for="ProjectMeta.Keywords"], span[class*="field-validation"], #ProjectMeta_Keywords ~ .text-danger, #ProjectMeta_Keywords ~ span');
                return span ? span.innerText : 'NO_SPAN_FOUND';
            }""")
            print(f"Val ({len(s)} chars): '{s}'\n  -> Result: {res}\n")

if __name__ == "__main__":
    find_failing_keywords()
