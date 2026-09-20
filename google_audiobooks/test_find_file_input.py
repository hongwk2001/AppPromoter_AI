import time
import json
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def find_created_input():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "content" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        # Click browse button
        browse_btn = page.locator('mat-dialog-container button[xapuploadertrigger], mat-dialog-container button:has-text("Browse")').first
        if browse_btn.count() > 0:
            print("Clicking Browse button...")
            browse_btn.click(force=True)
            time.sleep(1)

            # Inspect entire DOM (including hidden inputs)
            res = page.evaluate("""
            () => {
                const inps = Array.from(document.querySelectorAll('input'));
                return inps.map(i => ({
                    type: i.type,
                    id: i.id,
                    className: i.className,
                    outer: i.outerHTML
                }));
            }
            """)
            print("All Inputs in DOM:", json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    find_created_input()
