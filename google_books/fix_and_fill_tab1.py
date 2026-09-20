import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def fix_tab1(port=9222):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "info/" in pg.url]
        if not pages:
            pages = browser.contexts[0].pages
        page = pages[0]
        print(f"Connected to page: {page.url} ({page.title()})\n")

        # 1. Fill Title (mat-input-1)
        print("➡️ Filling Title...")
        title_inp = page.locator('#mat-input-1')
        if title_inp.count() > 0:
            title_inp.click()
            title_inp.fill("베오울프: 스펙터클 현대 한국어판")
            print("  ✓ Title set to: 베오울프: 스펙터클 현대 한국어판")

        # Check if Subtitle field exists, if not click "+ Add subtitle"
        sub_inp = page.locator('#mat-input-10, input[placeholder*="Subtitle" i]')
        if sub_inp.count() == 0 or not sub_inp.first.is_visible():
            add_sub_btn = page.locator('button:has-text("Subtitle"), [role="button"]:has-text("Subtitle")')
            if add_sub_btn.count() > 0:
                print("➡️ Clicking '+ Add subtitle' button...")
                add_sub_btn.first.click()
                time.sleep(1)

        # 2. Fill Subtitle
        print("➡️ Filling Subtitle...")
        sub_inp = page.locator('#mat-input-10, input[placeholder*="Subtitle" i]').first
        if sub_inp.count() > 0:
            sub_inp.click()
            sub_inp.fill("현대어 한국어 번역판")
            print("  ✓ Subtitle set to: 현대어 한국어 번역판")

        # 3. Fill Language (mat-input-3)
        print("➡️ Setting Language to Korean...")
        lang_inp = page.locator('#mat-input-3')
        if lang_inp.count() > 0:
            lang_inp.click()
            lang_inp.fill("Korean")
            time.sleep(1)
            opt = page.locator('mat-option:has-text("Korean"), [role="option"]:has-text("Korean")').first
            if opt.count() > 0:
                opt.click()
                print("  ✓ Language selected: Korean")
            else:
                print("  ⚠️ Mat option for Korean not found")

        # 4. Fill Publisher (mat-input-4)
        print("➡️ Filling Publisher...")
        pub_inp = page.locator('#mat-input-4')
        if pub_inp.count() > 0:
            pub_inp.click()
            pub_inp.fill("TKPROF LLC")
            print("  ✓ Publisher set to: TKPROF LLC")

        # 5. Fix Page Count (mat-input-7)
        print("➡️ Fixing Page Count...")
        page_inp = page.locator('#mat-input-7')
        if page_inp.count() > 0:
            page_inp.click()
            page_inp.fill("320")
            print("  ✓ Page count set to: 320")

        print("\n✨ Tab 1 clean fix complete! Check browser UI.")

if __name__ == "__main__":
    fix_tab1()
