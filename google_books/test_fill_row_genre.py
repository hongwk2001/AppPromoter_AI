"""
test_fill_row_genre.py
Adds a new genre row, selects 'GKSS (Korean)' scheme on that row,
types '영미소설' or '102', and clicks '(102) 영미소설'.
"""

import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_row_gkss():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page: {page.url}\n")

        # 1. Clear existing rows
        close_btns = page.locator('button:has-text("close")')
        while close_btns.count() > 0:
            try:
                close_btns.first.click()
                time.sleep(0.3)
            except Exception:
                break

        # 2. Click '+ Add a genre' button
        add_btn = page.locator('button:has-text("Add a genre"), [role="button"]:has-text("Add a genre")').first
        if add_btn.count() > 0:
            add_btn.click()
            time.sleep(1)

        # 3. Select 'GKSS (Korean)' scheme on new row
        scheme_select = page.locator('mat-select, [role="combobox"]').last
        if scheme_select.count() > 0:
            scheme_select.click()
            time.sleep(1)
            gk_opt = page.locator('mat-option:has-text("GKSS"), [role="option"]:has-text("GKSS")')
            if gk_opt.count() > 0:
                gk_opt.first.click()
                print("  ✓ Selected 'GKSS (Korean)' scheme on row")
                time.sleep(1)

        # 4. Type numeric code '102' into row input
        inp = page.locator('input[placeholder*="genre name or code" i], #mat-input-32, input[type="text"]').last
        if inp.count() > 0:
            inp.focus()
            inp.fill("")
            inp.type("102", delay=100)
            time.sleep(1.5)

            opts = page.locator('mat-option:has-text("102"), [role="option"]:has-text("102")')
            print(f"  Matching options count for '102': {opts.count()}")
            if opts.count() > 0:
                top_txt = opts.first.inner_text().strip().replace('\n', ' ')
                print(f"  ✓ Clicking matching option: '{top_txt}'")
                opts.first.click()
                time.sleep(1.5)

        # 5. Check warning status
        warn = page.locator('text="No genres added"')
        print(f"\n'No genres added' warning visible count: {warn.count()}")

if __name__ == "__main__":
    test_row_gkss()
