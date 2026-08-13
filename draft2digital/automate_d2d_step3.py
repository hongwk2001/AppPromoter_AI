"""
automate_d2d_step3.py
Automates Draft2Digital Step 3 (Pricing & Rights):
Populates Digital Book Price (USD), Library Price (USD),
and automatically checks ALL supported distribution channels (Kobo, Apple, Tolino, Vivlio, Smashwords, OverDrive, etc.).
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

def run_step3_autofill(book_name="the_enchanted_april", price="3.99", library_price="9.99", port=9222):
    print(f"\n🚀 Initiating Draft2Digital Step 3 (Pricing & Rights) Autofill")
    print(f"  Digital Book Price: ${price} USD")
    print(f"  Library Price:      ${library_price} USD\n")

    cdp_url = f"http://127.0.0.1:{port}"
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            print(f"Error connecting to Chrome on port {port}: {e}")
            return

        context = browser.contexts[0]
        page = None
        for p_obj in context.pages:
            if "draft2digital.com" in p_obj.url:
                page = p_obj
                break
                
        if not page:
            if context.pages:
                page = context.pages[0]
            else:
                print("Error: No browser tab available.")
                return

        print(f"Attached to page: {page.url} ({page.title()})")

        # 1. Fill Digital Book Price (#id_bookprice)
        if page.locator("#id_bookprice").count() > 0:
            page.locator("#id_bookprice").fill(str(price))
            print(f"  ✓ Filled Digital Book Price (#id_bookprice): ${price}")

        # 2. Fill Library Sale Price (#id_library-sale-price)
        if page.locator("#id_library-sale-price").count() > 0:
            page.locator("#id_library-sale-price").fill(str(library_price))
            print(f"  ✓ Filled Library Sale Price (#id_library-sale-price): ${library_price}")

        # 3. Select ALL Supported Distribution Channels (Kobo, Apple, Tolino, Vivlio, Smashwords, OverDrive, etc.)
        js_check_all = """
        () => {
            const targets = Array.from(document.querySelectorAll('div.toggle[aria-disabled="false"][aria-checked="false"], div[role="checkbox"][aria-disabled="false"][aria-checked="false"]'));
            const checked = [];
            targets.forEach(cb => {
                const tr = cb.closest('tr');
                const title = tr ? (tr.getAttribute('title') || tr.innerText.split('\\n')[0]) : 'Supported Channel';
                cb.click();
                checked.push(title);
            });
            return checked;
        }
        """
        checked_channels = page.evaluate(js_check_all)
        if checked_channels:
            print(f"  ✓ Checked {len(checked_channels)} supported distribution channels!")
        else:
            print("  ✓ All supported distribution channels are already selected.")

        print("\n✨ Draft2Digital Step 3 Pricing & Distribution Autofill Completed Successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate Draft2Digital Step 3 Pricing & Rights Entry")
    parser.add_argument("--book", type=str, default="the_enchanted_april")
    parser.add_argument("--price", type=str, default="3.99")
    parser.add_argument("--library-price", type=str, default="9.99")
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    run_step3_autofill(args.book, args.price, args.library_price, port=args.port)
