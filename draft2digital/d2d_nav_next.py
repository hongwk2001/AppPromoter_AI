"""
d2d_nav_next.py
Explicit Navigation Utility.
Clicks "Save & Continue" or approves layout/preview steps on Draft2Digital.
Only run when you have reviewed the page in your browser and want to proceed to the next step.
"""

import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def navigate_next(port=9222):
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "/book/" in pg.url]
        page = pages[0] if pages else [pg for pg in browser.contexts[0].pages if "draft2digital.com" in pg.url][0]
        print(f"\n Current Page: {page.url} ({page.title()})")

        # 1. Handle Layout page
        if "/layout" in page.url:
            print("  Navigating through Layout step...")
            save_btn = page.locator("#save-and-continue, a:has-text('SAVE & CONTINUE'), button:has-text('SAVE & CONTINUE'), .btn:has-text('SAVE & CONTINUE')")
            if save_btn.count() > 0:
                save_btn.first.click()
                print("  ✓ Clicked Save & Continue on Layout step!")
                time.sleep(4)

        # 2. Handle Preview page
        elif "/preview" in page.url:
            print("  Navigating through Preview step...")
            toggle = page.locator("#id_layout_approved, div.toggle")
            if toggle.count() > 0:
                try:
                    toggle.first.click()
                    time.sleep(1)
                except Exception:
                    pass
            js_check_all = """
            () => {
                const inputs = Array.from(document.querySelectorAll('input[type="checkbox"], input[type="radio"]'));
                inputs.forEach(inp => { if (!inp.checked) inp.click(); });
                const labels = Array.from(document.querySelectorAll('label'));
                labels.forEach(lbl => {
                    if (lbl.innerText.includes('approve') || lbl.innerText.includes('reviewed')) lbl.click();
                });
            }
            """
            page.evaluate(js_check_all)
            save_btn = page.locator(".submit-button, #save-and-continue, a:has-text('SAVE & CONTINUE'), button:has-text('SAVE & CONTINUE')")
            if save_btn.count() > 0:
                print("  Waiting for Preview submit button to become enabled...")
                try:
                    page.wait_for_selector(".submit-button:not([disabled]), #save-and-continue:not([disabled])", timeout=10000)
                except Exception:
                    pass
                page.evaluate(js_check_all)
                save_btn.first.click()
                print("  ✓ Clicked Save & Continue on Preview step!")
                time.sleep(5)

        # 3. Publish page check (SAFETY GUARD)
        elif "/publish" in page.url:
            print("  🛑 SAFETY STOP: Final Publish page reached (/publish).")
            print("     Auto-publishing is disabled per user request. Please review the page and click 'Publish My Book' manually.")
            return

        # 4. Standard Step 1 or Step 2 page
        else:
            save_btn = page.locator("#start-ebook-button, #save-and-continue, button:has-text('SAVE & CONTINUE'), a:has-text('SAVE & CONTINUE'), .btn:has-text('SAVE & CONTINUE')")
            if save_btn.count() > 0:
                btn_text = save_btn.first.inner_text().strip().lower()
                if "publish" in btn_text:
                    print("  🛑 SAFETY STOP: Detected Publish button. Auto-click disabled per user request.")
                    return
                print("  Waiting for Save & Continue button to be enabled...")
                try:
                    page.wait_for_selector("#save-and-continue:not([disabled]), #start-ebook-button:not([disabled])", timeout=120000)
                except Exception:
                    pass
                save_btn.first.click()
                print("  ✓ Clicked Save & Continue!")
                time.sleep(4)
            else:
                print("  ⚠️ Save & Continue button not found on this page.")

        pages = [pg for pg in browser.contexts[0].pages if "/book/" in pg.url]
        page = pages[0] if pages else [pg for pg in browser.contexts[0].pages if "draft2digital.com" in pg.url][0]
        print(f"\n➡️ New Page URL: {page.url} ({page.title()})")

if __name__ == "__main__":
    navigate_next()
