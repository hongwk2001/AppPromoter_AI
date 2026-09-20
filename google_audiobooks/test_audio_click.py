import time
import json
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_click():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "content" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page: {page.url}")

        btn = page.locator('button:has-text("Upload audio file"), [role="button"]:has-text("Upload audio file")').first
        if btn.count() > 0:
            print("Clicking 'Upload audio file' button...")
            btn.click(force=True)
            time.sleep(2)

            # Check if modal/overlay or file input appeared
            inputs = page.locator('input[type="file"]')
            print(f"File inputs count: {inputs.count()}")
            for i in range(inputs.count()):
                print(f"  Input [{i}]:", inputs.nth(i).evaluate("el => el.outerHTML"))

            # Check dialogs or overlays
            overlays = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('.cdk-overlay-container, [role="dialog"], mat-dialog-container')).map(d => ({
                    text: d.innerText.slice(0, 150),
                    outer: d.outerHTML.slice(0, 200)
                }));
            }
            """)
            print("Overlays:", json.dumps(overlays, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_click()
