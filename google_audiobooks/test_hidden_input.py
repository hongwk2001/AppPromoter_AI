import time
import json
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_hidden():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "content" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        # Inspect all input[type="file"] anywhere in the document including shadow DOM or dynamic bodies
        inputs_info = page.evaluate("""
        () => {
            const allInputs = Array.from(document.querySelectorAll('input'));
            const fileInputs = allInputs.filter(i => i.type === 'file' || i.getAttribute('accept') || i.outerHTML.includes('file'));
            return fileInputs.map(i => ({
                type: i.type,
                accept: i.accept,
                multiple: i.multiple,
                outer: i.outerHTML,
                parent: i.parentElement ? i.parentElement.tagName : null
            }));
        }
        """)

        print("Hidden file inputs:", json.dumps(inputs_info, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    check_hidden()
