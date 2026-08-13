"""
add_clean_contributors.py
Safely populates both TKPROF LLC (Translator) and TKPROF LLC (Editor) without clicking any page submit buttons.
"""

import os
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def add_clean():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]
        
        wrapper = page.locator("#contributors-field-wrapper")
        if wrapper.count() == 0:
            print("Wrapper not found.")
            return

        # 1. Expand section if button is visible
        open_btn = wrapper.locator('button:has-text("ADD NON-AUTHOR CONTRIBUTORS")')
        if open_btn.count() > 0 and open_btn.is_visible():
            open_btn.click()
            print("  ✓ Expanded Non-Author Contributors section")
            page.wait_for_timeout(600)

        roles = ["Translator", "Editor"]

        for role_name in roles:
            curr_text = wrapper.inner_text()
            if "TKPROF LLC" in curr_text and role_name in curr_text:
                print(f"  ✓ Contributor TKPROF LLC ({role_name}) is already added.")
                continue

            print(f"Adding TKPROF LLC as {role_name}...")

            # A. Select Name (#newContributorName)
            if page.locator("#newContributorName").count() > 0:
                page.locator("#newContributorName").click()
                page.wait_for_timeout(500)
                
                name_opt = page.locator("text='TKPROF LLC'")
                if name_opt.count() > 0:
                    name_opt.first.click()
                    print(f"  ✓ Selected name: TKPROF LLC")
                    page.wait_for_timeout(400)
                else:
                    add_new = page.locator("text='Add New Author', text='Add New'")
                    if add_new.count() > 0:
                        add_new.first.click()
                        page.wait_for_timeout(500)
                        inp = page.locator("#new-contributor")
                        if inp.count() > 0:
                            inp.fill("TKPROF LLC")
                            page.locator(".modal-body button").first.click()
                            page.wait_for_timeout(500)
                            print(f"  ✓ Created name in modal: TKPROF LLC")

            # B. Select Role (#newContributorRole)
            if page.locator("#newContributorRole").count() > 0:
                page.locator("#newContributorRole").click()
                page.wait_for_timeout(500)
                
                role_opt = page.locator(f"text='{role_name}'")
                if role_opt.count() > 0:
                    role_opt.first.click()
                    print(f"  ✓ Selected role: {role_name}")
                    page.wait_for_timeout(600)

        print("\nFinal Contributors Section Text:")
        print(wrapper.inner_text())

if __name__ == "__main__":
    add_clean()
