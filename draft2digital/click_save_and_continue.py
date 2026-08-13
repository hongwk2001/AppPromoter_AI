"""
click_save_and_continue.py
Clicks Save & Continue on Draft2Digital Step 2 to proceed to the next step (Pricing & Rights).
"""

import os
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def click_next():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]
        
        print(f"Current page before click: {page.url} ({page.title()})")
        
        save_btn = page.locator("#save-and-continue, button:has-text('SAVE & CONTINUE'), button:has-text('Save and Continue')")
        if save_btn.count() > 0:
            save_btn.first.click()
            print("  ✓ Clicked Save & Continue button!")
            page.wait_for_timeout(3000)
            
            # Re-fetch active page
            page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]
            print(f"\nNew Page URL: {page.url}")
            print(f"New Page Title: {page.title()}")
        else:
            print("  ⚠️ Save & Continue button not found.")

if __name__ == "__main__":
    click_next()
