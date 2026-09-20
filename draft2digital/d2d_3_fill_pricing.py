"""
d2d_3_fill_pricing.py
Populates Step 3 (Digital Price, Library Price, Channel Toggles, Preferences)
on active Draft2Digital page over CDP port 9222.
STOPS immediately after filling for user review — does NOT click Publish or move to next page.
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

def load_unified_metadata(book_name, lang="ko"):
    meta_path = os.path.join(NOTES_DIR, f"d2d_metadata_{book_name}_{lang}.json")
    if not os.path.exists(meta_path):
        from d2d_0_prepare_metadata import prepare_unified_metadata
        return prepare_unified_metadata(book_name, lang)
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def fill_step3(book_name, lang="ko", port=9222):
    data = load_unified_metadata(book_name, lang)
    if not data:
        print("Error: Could not load metadata.")
        return

    step3 = data["step3_pricing"]
    print(f"\n📋 Filling Step 3 (Pricing & Rights) for: {data['step1_metadata']['title']} ({lang.upper()})")
    print(f"  Digital Price: ${step3['digital_price_usd']} USD")
    print(f"  Library Price: ${step3['library_price_usd']} USD\n")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "/book/" in pg.url]
        page = pages[0] if pages else [pg for pg in browser.contexts[0].pages if "draft2digital.com" in pg.url][0]
        print(f"Active Tab: {page.url} ({page.title()})")

        # 1. Fill Digital Price
        if page.locator("#id_bookprice").count() > 0:
            page.locator("#id_bookprice").fill(str(step3["digital_price_usd"]))
            print(f"  ✓ Filled Digital Price (#id_bookprice): ${step3['digital_price_usd']}")

        # 2. Fill Library Price
        if page.locator("#id_library-sale-price").count() > 0:
            page.locator("#id_library-sale-price").fill(str(step3["library_price_usd"]))
            print(f"  ✓ Filled Library Price (#id_library-sale-price): ${step3['library_price_usd']}")

        # 3. Select Distribution Channels (based on target_stores config or enable all supported)
        t_stores = step3.get("target_stores", {})
        custom_states = t_stores.get("custom_store_states", {})

        js_set_stores = """
        (customStates) => {
            const rows = Array.from(document.querySelectorAll('tr'));
            const toggled = [];
            rows.forEach(tr => {
                const text = tr.innerText.trim();
                if (!text) return;
                const storeName = text.split('\\n')[0].trim();
                const cb = tr.querySelector('div.toggle, div[role="checkbox"], input[type="checkbox"]');
                if (!cb) return;

                const isDisabled = cb.getAttribute('aria-disabled') === 'true' || cb.disabled === true;
                if (isDisabled) return;

                const isChecked = cb.getAttribute('aria-checked') === 'true' || cb.checked === true;
                
                // If custom state specified in JSON
                if (storeName in customStates) {
                    const targetState = customStates[storeName];
                    if (targetState !== isChecked) {
                        cb.click();
                        toggled.push(`${storeName}: ${targetState}`);
                    }
                } else {
                    // Default to checking supported enabled channels
                    if (!isChecked) {
                        cb.click();
                        toggled.push(storeName);
                    }
                }
            });
            return toggled;
        }
        """
        toggled_stores = page.evaluate(js_set_stores, custom_states)
        if toggled_stores:
            print(f"  ✓ Updated {len(toggled_stores)} distribution channel states!")
        else:
            print("  ✓ Distribution channel states match target JSON configuration.")

        # 4. Check "Remember my store preferences"
        if step3.get("remember_store_preferences", True):
            pref_label = page.locator("label:has-text('Remember my store preferences')")
            if pref_label.count() > 0:
                try:
                    pref_label.first.click()
                    print("  ✓ Checked 'Remember my store preferences'")
                except Exception:
                    pass

        print("\n✨ Step 3 Autofill Finished! (Form populated — Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill Step 3 Form Fields & Pause for Review")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    fill_step3(args.book, args.lang, port=args.port)
