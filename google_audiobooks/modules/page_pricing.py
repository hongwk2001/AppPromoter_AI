import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def fill_pricing_page(page, price="9.99"):
    print("\n--- [Module: Pricing Page] ---")

    # Dismiss dialog if open
    cancel_btn = page.locator('mat-dialog-container button:has-text("Cancel")').first
    if cancel_btn.count() > 0 and cancel_btn.is_visible():
        cancel_btn.click(force=True)
        time.sleep(1)

    # Clean empty price rows
    remove_btns = page.locator('button[aria-label*="Remove" i], button:has-text("close")')
    while remove_btns.count() > 1:
        try:
            remove_btns.last.click(force=True)
            time.sleep(0.5)
            remove_btns = page.locator('button[aria-label*="Remove" i], button:has-text("close")')
        except Exception:
            break

    # Fill price row 0
    price_inps = page.locator('mat-form-field:has-text("Price") input, input[placeholder*="Price" i], input[type="number"]')
    if price_inps.count() == 0:
        add_price_btn = page.locator('button:has-text("Add a price"), [role="button"]:has-text("Add a price")').first
        if add_price_btn.count() > 0 and add_price_btn.is_visible():
            add_price_btn.click(force=True)
            time.sleep(1)
            price_inps = page.locator('mat-form-field:has-text("Price") input, input[placeholder*="Price" i], input[type="number"]')

    if price_inps.count() > 0:
        print(f"➡️ Setting Price: {price}")
        price_inps.first.click(force=True)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        price_inps.first.fill(str(price))
        time.sleep(0.5)

    print("✨ Pricing Page populated cleanly (Save button not clicked as instructed)!")
