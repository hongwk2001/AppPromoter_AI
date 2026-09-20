import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_dom():
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
            const getFieldInfo = (segmentId) => {
                const input = document.querySelector(`input[data-segment-id="${segmentId}"]`);
                if (!input) return null;
                const parent = input.closest('.form-group, .mb-3, tr, td, div');
                const label = parent ? parent.innerText.trim().replace(/\\s+/g, ' ') : '';
                const buttons = parent ? Array.from(parent.querySelectorAll('button, a, label, input')).map(b => ({
                    tag: b.tagName,
                    id: b.id,
                    class: b.className,
                    text: b.innerText || b.value
                })) : [];
                return {
                    segmentId: segmentId,
                    inputId: input.id,
                    inputClass: input.className,
                    parentText: label.substring(0, 200),
                    elements: buttons
                };
            };

            return {
                opening: getFieldInfo("1"),
                closing: getFieldInfo("2"),
                sample: getFieldInfo("3"),
                chapters: getFieldInfo("0")
            };
        }""")

        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    inspect_dom()
