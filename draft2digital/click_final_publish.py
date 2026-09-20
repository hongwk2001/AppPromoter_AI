"""
click_final_publish.py
SAFETY MODE ENFORCED: Auto-publishing is explicitly DISABLED.
This script will inspect form elements but WILL NOT click the final Publish button.
"""

import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def publish():
    print("\n🛑 SAFETY NOTICE: Final publishing auto-click is DISABLED.")
    print("   Per user safety settings, books will remain in draft mode.")
    print("   Please review the populated page in your browser and click 'Publish My Book' manually.\n")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            pages = [pg for pg in context.pages if "/book/" in pg.url]
            if not pages:
                print("No active /book/ tab found.")
                return
            page = pages[0]
            print(f"Current Page: {page.url} ({page.title()})")
            
            pub_btn = page.locator("#publish_submit_button, #publish-book, #submit-for-publishing, button:has-text('Publish'), button:has-text('PUBLISH'), a:has-text('Publish')")
            if pub_btn.count() > 0:
                print(f"  ℹ️ Found Publish button '{pub_btn.first.inner_text().strip()}' — NOT CLICKED (Safety Guard Active).")
        except Exception as e:
            print(f"Error inspecting page: {e}")

if __name__ == "__main__":
    publish()
