import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_radios():
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
            print("No authorsrepublic page found.")
            return

        radios = page.evaluate("""() => {
            const inputs = Array.from(document.querySelectorAll('input[type="radio"]'));
            return inputs.map(r => {
                let parentText = r.parentElement ? r.parentElement.innerText.trim() : '';
                let labelText = r.labels && r.labels[0] ? r.labels[0].innerText.trim() : '';
                return {
                    id: r.id,
                    name: r.name,
                    value: r.value,
                    checked: r.checked,
                    labelText: labelText,
                    parentText: parentText
                };
            });
        }""")

        print(json.dumps(radios, indent=2))

if __name__ == "__main__":
    inspect_radios()
