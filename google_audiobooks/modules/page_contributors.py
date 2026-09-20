import os
import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def fill_contributors_page(page, contributors):
    print("\n--- [Module: Contributors Page] ---")

    # Dismiss dialog if open
    cancel_btn = page.locator('mat-dialog-container button:has-text("Cancel")').first
    if cancel_btn.count() > 0 and cancel_btn.is_visible():
        cancel_btn.click(force=True)
        time.sleep(1)

    def clean_empty_contributor_rows():
        page.evaluate("""() => {
            const formFields = Array.from(document.querySelectorAll('mat-form-field'));
            formFields.forEach(ff => {
                const inp = ff.querySelector('input:not([data-formula])');
                if (inp && inp.value.trim() === '' && ff.innerText.toLowerCase().includes('name')) {
                    const parent = ff.closest('div, tr, mat-card, form') || ff.parentElement;
                    const btn = parent ? parent.querySelector('button') : null;
                    if (btn) btn.click();
                }
            });
        }""")
        time.sleep(0.5)

    # 1. Clean empty rows first
    clean_empty_contributor_rows()

    # 2. Fill contributor rows
    for idx, contrib in enumerate(contributors):
        name = contrib.get("name")
        role = contrib.get("role")
        bio = contrib.get("bio", "")

        name_inps = page.locator('input.mat-mdc-input-element:not([data-formula])')
        if name_inps.count() <= idx:
            add_btn = page.locator('button:has-text("Add a contributor"), [role="button"]:has-text("Add a contributor")').first
            if add_btn.count() > 0 and add_btn.is_visible():
                print("➡️ Clicking Add a contributor...")
                add_btn.click(force=True)
                time.sleep(1)

        name_inps = page.locator('input.mat-mdc-input-element:not([data-formula])')
        if name_inps.count() > idx:
            print(f"➡️ Contributor [{idx+1}] Name: {name}")
            name_inps.nth(idx).click(force=True)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            name_inps.nth(idx).fill(name)
            time.sleep(0.5)

        role_sel = page.locator('mat-form-field:has-text("Role") mat-select, mat-select')
        if role_sel.count() > idx:
            print(f"➡️ Contributor [{idx+1}] Role: {role}")
            role_sel.nth(idx).click(force=True)
            time.sleep(0.5)
            opt = page.locator(f'mat-option:has-text("{role}")').first
            if opt.count() > 0:
                print(f"  ✓ Clicked role option: {opt.inner_text().strip()}")
                opt.click(force=True)
                time.sleep(0.5)

        bio_inps = page.locator('.ql-editor, textarea[aria-label*="biography" i], textarea[aria-label*="Bio" i]')
        if bio_inps.count() > idx and bio:
            print(f"  ➡️ Contributor [{idx+1}] Bio filled.")
            bio_inps.nth(idx).click(force=True)
            bio_inps.nth(idx).fill(bio)
            time.sleep(0.5)

        if role == "Narrator":
            synth_radio = page.locator('mat-radio-button:has-text("Synthesized voice"), mat-radio-button:has-text("AI")').first
            if synth_radio.count() > 0 and synth_radio.is_visible():
                print("  ➡️ Selecting Synthesized voice radio button...")
                synth_radio.click(force=True)
                time.sleep(0.5)

    # 3. Clean empty rows after filling
    clean_empty_contributor_rows()

    print("✨ Contributors Page populated cleanly (Save button not clicked as instructed)!")
