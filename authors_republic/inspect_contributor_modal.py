import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_contrib():
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

        contrib_buttons = page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('a, button, span, div')).filter(el => {
                const text = el.innerText.trim();
                return text.includes('Add Author') || text.includes('Add Narrator') || text.includes('Add Contributor');
            });

            return btns.map(b => ({
                tag: b.tagName.toLowerCase(),
                id: b.id,
                class: b.className,
                text: b.innerText.trim(),
                onclick: b.getAttribute('onclick'),
                dataTarget: b.getAttribute('data-target') || b.getAttribute('data-bs-target')
            }));
        }""")

        print("Contributor Buttons found:")
        for b in contrib_buttons:
            print(f" Tag: <{b['tag']}> | ID: '{b['id']}' | Class: '{b['class']}' | Text: '{b['text']}' | OnClick: '{b['onclick']}' | Target: '{b['dataTarget']}'")

if __name__ == "__main__":
    inspect_contrib()
