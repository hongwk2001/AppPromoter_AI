"""
test_keyboard_select.py
Tests selecting Angular Material autocomplete option using keyboard sequence (ArrowDown + Enter),
then clicking '+ Add a genre'.
"""

import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page: {page.url}\n")

        inp = page.locator('input[placeholder*="genre name or code" i], #mat-input-32').first
        if inp.count() > 0:
            print("1. Focusing input and typing '102'...")
            inp.focus()
            inp.fill("")
            inp.type("102", delay=100)
            time.sleep(1.5)

            print("2. Pressing ArrowDown to select option in Angular autocomplete...")
            page.keyboard.press("ArrowDown")
            time.sleep(0.5)

            print("3. Pressing Enter to confirm option selection...")
            page.keyboard.press("Enter")
            time.sleep(1)

            print("4. Clicking '+ Add a genre' button...")
            add_btn = page.locator('button:has-text("Add a genre"), [role="button"]:has-text("Add a genre")').first
            add_btn.click()
            time.sleep(2)

        # Inspect if warning disappeared or genre row added
        warn = page.locator('text="No genres added"')
        print(f"\n'No genres added' warning visible count: {warn.count()}")

if __name__ == "__main__":
    run_test()
