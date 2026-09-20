import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_keywords():
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

        test_strings = [
            "Richest Man in Babylon;personal finance;George S. Clason;money;investing;audiobook;wealth;classics",
            "Richest Man in Babylon; personal finance; George S. Clason; money; investing; audiobook; wealth",
            "Richest Man in Babylon; personal finance; George Clason; money; investing; audiobook; wealth",
            "Richest Man in Babylon; personal finance; money; investing; audiobook; wealth; classics",
            "babylon; finance; money; investing; audiobook; wealth; classics",
            "personal finance; money; investing; wealth; classic; babylon"
        ]

        for s in test_strings:
            page.fill("#ProjectMeta_Keywords", s)
            page.evaluate("document.querySelector('#ProjectMeta_Keywords').dispatchEvent(new Event('change'))")
            page.evaluate("document.querySelector('#ProjectMeta_Keywords').dispatchEvent(new Event('blur'))")
            
            # Check for error text below input
            err = page.evaluate("""() => {
                const el = document.querySelector('#ProjectMeta_Keywords');
                const errSpan = el.parentElement.querySelector('.field-validation-error, .text-danger, span[data-valmsg-for="ProjectMeta.Keywords"]');
                return errSpan ? errSpan.innerText.trim() : '';
            }""")
            print(f"Testing length={len(s)}: '{s}' -> Error: '{err}'")

if __name__ == "__main__":
    test_keywords()
