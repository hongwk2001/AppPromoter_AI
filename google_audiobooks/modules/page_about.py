import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def fill_about_page(page, book_info):
    print("\n--- [Module: About Page] ---")

    # Dismiss dialog if open
    cancel_btn = page.locator('mat-dialog-container button:has-text("Cancel"), mat-dialog-container button:has-text("OK")').first
    if cancel_btn.count() > 0 and cancel_btn.is_visible():
        cancel_btn.click(force=True)
        time.sleep(1)

    sub_btn = page.locator('button:has-text("Add a subtitle"), [role="button"]:has-text("Add a subtitle"), a:has-text("Add a subtitle")').first
    if sub_btn.count() > 0 and sub_btn.is_visible():
        sub_btn.click(force=True)
        time.sleep(0.8)

    inps = page.locator('input.mat-mdc-input-element')
    if inps.count() >= 1 and book_info.get('title'):
        print(f"➡️ Setting Title: {book_info.get('title')}")
        inps.nth(0).click(force=True)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        inps.nth(0).fill(book_info.get('title'))
        time.sleep(0.5)

    if inps.count() >= 2 and book_info.get('subtitle'):
        print(f"➡️ Setting Subtitle: {book_info.get('subtitle')}")
        inps.nth(1).click(force=True)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        inps.nth(1).fill(book_info.get('subtitle'))
        time.sleep(0.5)

    dur_inp = page.locator('mat-form-field:has-text("Duration") input, input[placeholder*="HH:MM:SS" i]').first
    if dur_inp.count() > 0 and book_info.get('duration'):
        print(f"➡️ Setting Duration: {book_info.get('duration')}")
        dur_inp.click(force=True)
        dur_inp.fill(book_info.get('duration'))
        time.sleep(0.5)

    desc_editor = page.locator('.ql-editor, textarea[aria-label*="Description" i]').first
    if desc_editor.count() > 0 and book_info.get('description'):
        print("➡️ Filling Description...")
        desc_editor.click(force=True)
        desc_editor.fill(book_info.get('description'))
        time.sleep(0.5)

    print("✨ About Page populated cleanly (Save button not clicked as instructed)!")
