"""
save_store_preferences.py
Checks "Remember my store preferences" on Draft2Digital Step 3.
"""

import os
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def save_preferences():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]
        
        pref_label = page.locator("label:has-text('Remember my store preferences')")
        if pref_label.count() > 0:
            pref_label.first.click()
            print("  ✓ Clicked 'Remember my store preferences'")
        else:
            pref_cb = page.locator("input[name*='remember'], input[id*='remember']")
            if pref_cb.count() > 0:
                pref_cb.first.click()
                print("  ✓ Checked 'Remember my store preferences' checkbox")
            else:
                print("  ⚠️ Could not find 'Remember my store preferences' checkbox.")

        page.wait_for_timeout(500)

if __name__ == "__main__":
    save_preferences()
