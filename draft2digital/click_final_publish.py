"""
click_final_publish.py
Inspects and clicks the final Publish / Submit button on Draft2Digital.
"""

import sys
import time
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def publish():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]
        print(f"Current Page: {page.url} ({page.title()})")
        
        js = """
        () => {
            const btns = Array.from(document.querySelectorAll('button, input[type="submit"], a.btn, input[type="checkbox"], label'));
            return btns.map(b => ({
                tag: b.tagName.toLowerCase(),
                id: b.id || '',
                class: b.className || '',
                type: b.type || '',
                text: (b.innerText || b.value || '').trim(),
                visible: !!(b.offsetWidth || b.offsetHeight || b.getClientRects().length)
            })).filter(b => b.visible && (b.text.includes('Publish') || b.text.includes('PUBLISH') || b.text.includes('Submit') || b.text.includes('rights') || b.text.includes('agree') || b.type === 'checkbox'));
        }
        """
        elements = page.evaluate(js)
        print("Interactive publish elements:")
        print(json.dumps(elements, indent=2, ensure_ascii=False))
        
        # Check any terms/rights agreement checkboxes
        chk_js = """
        () => {
            const cbs = Array.from(document.querySelectorAll('input[type="checkbox"]'));
            let count = 0;
            cbs.forEach(cb => {
                if (!cb.checked) {
                    cb.click();
                    count++;
                }
            });
            return count;
        }
        """
        c_count = page.evaluate(chk_js)
        if c_count > 0:
            print(f"  ✓ Checked {c_count} terms/rights agreement checkboxes")
            time.sleep(1)

        pub_btn = page.locator("#publish_submit_button, #publish-book, #submit-for-publishing, button:has-text('Publish'), button:has-text('PUBLISH'), a:has-text('Publish')")
        if pub_btn.count() > 0:
            print("  Found Publish button! Clicking...")
            pub_btn.first.click()
            print("  ✓ Clicked final Publish button!")
            time.sleep(5)
            page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]
            print(f"\nFinal URL after publish: {page.url}")
            print(f"Final Title: {page.title()}")
        else:
            print("  ⚠️ Publish button not found on current page.")

if __name__ == "__main__":
    publish()
