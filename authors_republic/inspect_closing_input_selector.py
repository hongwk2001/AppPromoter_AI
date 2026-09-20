import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_closing():
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
            const inputs = Array.from(document.querySelectorAll('input.chunkUploader'));
            return inputs.map(i => {
                const segId = i.getAttribute('data-segment-id');
                const p = i.parentElement;
                const grandP = p ? p.parentElement : null;
                const label = p ? p.querySelector('label') : null;
                const grandLabel = grandP ? grandP.querySelector('label') : null;
                
                return {
                    segmentId: segId,
                    inputOuterHTML: i.outerHTML,
                    parentTagName: p ? p.tagName : '',
                    parentClass: p ? p.className : '',
                    hasLabelInParent: !!label,
                    hasLabelInGrandParent: !!grandLabel,
                    labelHTML: label ? label.outerHTML : (grandLabel ? grandLabel.outerHTML : 'NO_LABEL')
                };
            });
        }""")

        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    inspect_closing()
