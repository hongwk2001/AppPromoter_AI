"""
interactive_add_genre.py
Interactively searches, selects, and commits GKSS genre 102 on Google Books.
"""

import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def run_interactive():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page: {page.url}\n")

        # 1. Focus and fill input with '102'
        inp = page.locator('input[placeholder*="genre name or code" i], #mat-input-32').first
        print(f"1. Input element count: {inp.count()}")
        inp.focus()
        inp.fill("102")
        time.sleep(1.5)

        # 2. Wait for mat-option overlay
        opts = page.locator('mat-option')
        print(f"2. mat-option count: {opts.count()}")
        for i in range(opts.count()):
            txt = opts.nth(i).inner_text().strip()
            print(f"   Option [{i+1}]: {txt}")
            if "102" in txt or "영미소설" in txt:
                print(f"3. Clicking option: {txt}")
                opts.nth(i).click()
                time.sleep(1)
                break

        # 3. Press Enter key on input to commit option
        print("4. Pressing Enter key on genre input...")
        inp.focus()
        inp.press("Enter")
        time.sleep(1.5)

        # 4. Also click '+ Add a genre' button if still visible
        add_btn = page.locator('button:has-text("Add a genre"), button:has-text("Add")')
        print(f"5. Add button count: {add_btn.count()}")
        if add_btn.count() > 0 and add_btn.first.is_visible():
            print("6. Clicking '+ Add a genre' button...")
            add_btn.first.click()
            time.sleep(2)

        # 5. Check warning visibility
        warn = page.locator('text="No genres added"')
        print(f"7. 'No genres added' warning visible count: {warn.count()}")

if __name__ == "__main__":
    run_interactive()
