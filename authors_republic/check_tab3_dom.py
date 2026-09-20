import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_tab3_dom():
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
            const inputs = Array.from(document.querySelectorAll('input.chunkUploader, input[data-segment-id]'));
            return inputs.map(i => {
                const segId = i.getAttribute('data-segment-id');
                const container = i.closest('.form-group, .mb-3, tr, td, div');
                const valInput = container ? container.querySelector('input[type="hidden"], input[type="text"]') : null;
                const fileList = container ? Array.from(container.querySelectorAll('.qq-upload-file, .file-name, span')).map(s => s.innerText.trim()).filter(Boolean) : [];
                return {
                    segmentId: segId,
                    value: i.value,
                    filesText: fileList,
                    containerText: container ? container.innerText.trim().replace(/\\s+/g, ' ').substring(0, 150) : ''
                };
            });
        }""")

        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    check_tab3_dom()
