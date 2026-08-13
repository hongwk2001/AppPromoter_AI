"""
handle_layout_and_preview.py
Navigates through D2D layout and preview steps to arrive at Step 3 (Rights & Pricing).
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def navigate_layout_and_preview():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]
        print(f"Current page: {page.url} ({page.title()})")
        
        # 1. Handle Layout page if active
        if "/layout" in page.url:
            print("Processing Layout page...")
            save_btn = page.locator("#save-and-continue, a:has-text('SAVE & CONTINUE'), button:has-text('SAVE & CONTINUE'), .btn:has-text('SAVE & CONTINUE')")
            if save_btn.count() > 0:
                save_btn.first.click()
                print("  ✓ Clicked Save & Continue on Layout page!")
                time.sleep(4)
                page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]
                print(f"  Navigated to: {page.url} ({page.title()})")

        # 2. Handle Preview page if active
        if "/preview" in page.url:
            print("Processing Preview page...")
            # Check all approval checkboxes / inputs on page
            js_check_all = """
            () => {
                const inputs = Array.from(document.querySelectorAll('input[type="checkbox"], input[type="radio"]'));
                let count = 0;
                inputs.forEach(inp => {
                    if (!inp.checked) {
                        inp.click();
                        count++;
                    }
                });
                const labels = Array.from(document.querySelectorAll('label'));
                labels.forEach(lbl => {
                    if (lbl.innerText.includes('approve') || lbl.innerText.includes('reviewed') || lbl.innerText.includes('I have')) {
                        lbl.click();
                    }
                });
                return count;
            }
            """
            c_count = page.evaluate(js_check_all)
            print(f"  ✓ Checked {c_count} approval elements on Preview page")
            
            save_btn = page.locator(".submit-button, #save-and-continue, a:has-text('SAVE & CONTINUE'), button:has-text('SAVE & CONTINUE'), .btn:has-text('SAVE & CONTINUE')")
            if save_btn.count() > 0:
                print("  Waiting for Preview submit button to become enabled (rendering MOBI/EPUB preview)...")
                try:
                    page.wait_for_selector(".submit-button:not([disabled]), #save-and-continue:not([disabled])", timeout=120000)
                except Exception as e:
                    print(f"  Notice during wait: {e}")
                
                # Re-check checkboxes after preview render
                page.evaluate(js_check_all)
                save_btn.first.click()
                print("  ✓ Clicked Save & Continue on Preview page!")
                time.sleep(5)
                page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]
                print(f"\nFinal Page URL: {page.url}")
                print(f"Final Page Title: {page.title()}")

if __name__ == "__main__":
    navigate_layout_and_preview()
