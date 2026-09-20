"""
google_3_fill_pricing.py
Populates Pricing (Price, Currency, World Rights) on active Google Books Partner Center tab over CDP port 9222.
STOPS immediately after filling for user review — does NOT click Publish or Save.
"""

import os
import sys
import json
import argparse
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def load_google_metadata(book_name, lang="ko"):
    audio_path = os.path.join(NOTES_DIR, f"google_audio_metadata_{book_name}_{lang}.json")
    if os.path.exists(audio_path):
        with open(audio_path, "r", encoding="utf-8") as f:
            return json.load(f)
    meta_path = os.path.join(NOTES_DIR, f"google_metadata_{book_name}_{lang}.json")
    if not os.path.exists(meta_path):
        from google_0_prepare_metadata import prepare_google_metadata
        return prepare_google_metadata(book_name, lang)
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def fill_pricing(book_name, lang="ko", port=9222):
    data = load_google_metadata(book_name, lang)
    if not data:
        print("Error: Could not load Google Books metadata.")
        return

    pricing = data.get("pricing", {})
    price_val = pricing.get("digital_price_usd") or pricing.get("price_usd") or "14.99"
    currency_val = pricing.get("currency", "USD")
    title = data.get("tab1_about_the_book", data.get("book_info", {})).get("title", book_name)
    print(f"\n📋 Filling Google Books Pricing for: {title} ({lang.upper()})")
    print(f"  Price:    ${price_val} {currency_val}")
    print(f"  Rights:   World Rights (WORLD)\n")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return
        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "/pricing" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        # Switch to Pricing tab if needed
        if "/pricing" not in page.url:
            price_tab = page.locator('a[href*="pricing"], a:has-text("Pricing"), span:has-text("Pricing")')
            if price_tab.count() > 0:
                print("➡️ Switching to Pricing tab...")
                price_tab.first.click(force=True)
                page.wait_for_timeout(1500)

        print(f"Active Tab: {page.url} ({page.title()})")

        # 1. Fill Digital Price
        price_loc = page.locator('input[aria-label*="Price" i], input[placeholder*="Price" i], input[name*="price" i]')
        if price_loc.count() > 0:
            price_loc.first.fill(str(price_val))
            print(f"  ✓ Filled Price: ${price_val}")

        # 2. Fill Currency (USD)
        curr_loc = page.locator('input[aria-label*="Currency" i], select[aria-label*="Currency" i]')
        if curr_loc.count() > 0:
            try:
                curr_loc.first.fill(currency_val)
                print(f"  ✓ Filled Currency: {currency_val}")
            except Exception:
                pass

        # 3. Check World Rights
        if pricing.get("world_rights", True):
            world_cb = page.locator('input[type="checkbox"][aria-label*="World" i], label:has-text("World"), label:has-text("WORLD")')
            if world_cb.count() > 0:
                try:
                    world_cb.first.click()
                    print("  ✓ Checked World Distribution Rights")
                except Exception:
                    pass

        print("\n✨ Google Books Pricing Form Populated! (Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill Google Books Pricing & Pause for Review")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    fill_pricing(args.book, args.lang, port=args.port)
