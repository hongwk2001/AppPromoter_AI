"""
set_row_gkss_and_add.py
Sets GKSS scheme on the new genre row and adds (102) 영미소설, (106) 동서양고전, (100) 소설.
"""

import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

GKSS_ITEMS = [
    {"code": "102", "name": "영미소설"},
    {"code": "106", "name": "동서양고전"},
    {"code": "100", "name": "소설"}
]

def run_set_gkss():
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

        for item in GKSS_ITEMS:
            print(f"\n➡️ Adding GKSS Genre: {item['code']} ({item['name']})...")
            
            # Click '+ Add a genre'
            add_btn = page.locator('button:has-text("Add a genre"), [role="button"]:has-text("Add a genre")').first
            if add_btn.count() > 0:
                add_btn.click()
                time.sleep(1)

            # Select GKSS scheme on the latest mat-select
            mat_selects = page.locator('mat-select, [role="combobox"]')
            if mat_selects.count() > 0:
                target_select = mat_selects.last
                target_select.click()
                time.sleep(1)

                gk_opt = page.locator('mat-option:has-text("GKSS"), [role="option"]:has-text("GKSS")')
                if gk_opt.count() > 0:
                    gk_opt.first.click()
                    print("  ✓ Selected 'GKSS (Korean)' scheme")
                    time.sleep(1)

            # Type code in the latest input
            row_inps = page.locator('input[placeholder*="genre name or code" i], #mat-input-32, input[type="text"]')
            if row_inps.count() > 0:
                target_inp = row_inps.last
                target_inp.focus()
                target_inp.fill("")
                target_inp.type(item['code'], delay=100)
                time.sleep(1.5)

                # Match option containing both code and Korean name
                opts = page.locator(f'mat-option:has-text("{item["code"]}"), mat-option:has-text("{item["name"]}")')
                if opts.count() > 0:
                    top_txt = opts.first.inner_text().strip().replace('\n', ' ')
                    print(f"  ✓ Clicking option: '{top_txt}'")
                    opts.first.click()
                    time.sleep(1.5)

        # Check warning status
        warn = page.locator('text="No genres added"')
        print(f"\n'No genres added' warning visible count: {warn.count()}")

if __name__ == "__main__":
    run_set_gkss()
