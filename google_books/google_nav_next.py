"""
google_nav_next.py
Explicit Navigation Utility for Google Books Partner Center.
Clicks Next or Save on the active Google Books tab.
Only run when you have reviewed the page in Chrome and want to proceed to the next step.
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

        pages = [pg for pg in browser.contexts[0].pages if "play.google.com/books" in pg.url or "google.com" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"\n Current Page: {page.url} ({page.title()})")

        next_btn = page.locator('button:has-text("Save & Continue"), button:has-text("Save"), button:has-text("Next"), button:has-text("Continue"), [role="button"]:has-text("Next")')
        if next_btn.count() > 0:
            next_btn.first.click()
            print("  ✓ Clicked Next/Save button on Google Books!")
            time.sleep(3)
        else:
            print("  ⚠️ Next/Save button not found on this page.")

        pages = [pg for pg in browser.contexts[0].pages if "play.google.com/books" in pg.url or "google.com" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"➡️ New Page URL: {page.url} ({page.title()})")

if __name__ == "__main__":
    navigate_next()
