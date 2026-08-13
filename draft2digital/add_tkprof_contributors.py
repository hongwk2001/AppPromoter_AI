"""
add_tkprof_contributors.py
Expands Non-Author Contributors and adds TKPROF LLC as Translator and Editor into D2D Step 2.
"""

import os
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def add_contributors():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]
        
        wrapper = page.locator("#contributors-field-wrapper")
        if wrapper.count() == 0:
            print("Contributors wrapper not found.")
            return

        # 1. Click 'ADD NON-AUTHOR CONTRIBUTORS' if visible
        open_btn = wrapper.locator('button:has-text("ADD NON-AUTHOR CONTRIBUTORS")')
        if open_btn.count() > 0 and open_btn.is_visible():
            open_btn.click()
            print("  ✓ Clicked ADD NON-AUTHOR CONTRIBUTORS button!")
            page.wait_for_timeout(800)

        roles = ["Translator", "Editor"]

        for role_name in roles:
            curr_text = wrapper.inner_text()
            if "TKPROF LLC" in curr_text and role_name in curr_text:
                print(f"  ✓ {role_name} already added.")
                continue

            print(f"\nAdding TKPROF LLC as {role_name}...")
            
            # Select Name (#newContributorName)
            page.locator("#newContributorName").click()
            page.wait_for_timeout(600)
            
            tkprof_name = page.locator("text='TKPROF LLC'")
            if tkprof_name.count() > 0:
                tkprof_name.first.click()
                print("  ✓ Selected name: TKPROF LLC")
                page.wait_for_timeout(400)

            # Select Role (#newContributorRole)
            page.locator("#newContributorRole").click()
            page.wait_for_timeout(600)
            
            role_opt = page.locator(f"text='{role_name}'")
            if role_opt.count() > 0:
                role_opt.first.click()
                print(f"  ✓ Selected role: {role_name}")
                page.wait_for_timeout(400)

            # Click the plus/add button next to the input row
            # On D2D, selecting both Name and Role triggers an automatic add OR reveals a plus icon
            add_icon = wrapper.locator('i.fa-plus, button:has-text("+"), .add-item, button.btn-primary')
            if add_icon.count() > 0 and add_icon.first.is_visible():
                add_icon.first.click()
                print(f"  ✓ Clicked Add (+) for {role_name}")
                page.wait_for_timeout(800)

        print("\nFinal Contributors Section Text:")
        print(wrapper.inner_text())

if __name__ == "__main__":
    add_contributors()
