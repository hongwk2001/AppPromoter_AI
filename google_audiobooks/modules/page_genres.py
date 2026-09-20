import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def fill_genres_page(page, book_info, lang="ko"):
    print("\n--- [Module: Genres Page] ---")

    # Dismiss dialog if open
    cancel_btn = page.locator('mat-dialog-container button:has-text("Cancel")').first
    if cancel_btn.count() > 0 and cancel_btn.is_visible():
        cancel_btn.click(force=True)
        time.sleep(1)

    def clean_empty_genre_rows():
        page.evaluate("""() => {
            const formFields = Array.from(document.querySelectorAll('mat-form-field'));
            formFields.forEach(ff => {
                const inp = ff.querySelector('input');
                if (inp && (inp.value.trim() === '' || inp.value.toLowerCase().includes('invalid'))) {
                    // Find close button near this field
                    const parent = ff.closest('div, tr, mat-card, form') || ff.parentElement;
                    const btn = parent ? parent.querySelector('button') : null;
                    if (btn) btn.click();
                }
            });
        }""")
        time.sleep(0.5)

    # 1. Clean empty rows first
    clean_empty_genre_rows()

    categories = book_info.get('categories', [])
    for idx, cat in enumerate(categories):
        # Check if already filled
        inps = page.locator('mat-form-field input, input[placeholder*="Genre" i]')
        if inps.count() <= idx:
            add_btn = page.locator('button:has-text("Add a genre"), [role="button"]:has-text("Add a genre")').first
            if add_btn.count() > 0 and add_btn.is_visible():
                add_btn.click(force=True)
                time.sleep(1)

        scheme = book_info.get("subject_scheme", "BISAC") if lang == "en" else "GKSS"
        sel = page.locator('mat-select')
        if sel.count() > idx and scheme not in sel.nth(idx).inner_text():
            sel.nth(idx).click(force=True)
            time.sleep(0.5)
            opt = page.locator(f'mat-option:has-text("{scheme}")').first
            if opt.count() > 0:
                opt.click(force=True)
                time.sleep(0.5)

        inps = page.locator('mat-form-field input, input[placeholder*="Genre" i]')
        if inps.count() > idx:
            query = cat.split("/")[-1].strip()
            print(f"➡️ Setting Genre [{idx+1}]: {query}")
            inps.nth(idx).click(force=True)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            inps.nth(idx).fill(query)
            time.sleep(1.5)

            opts = page.locator('mat-option')
            if opts.count() > 0:
                prefix = cat.split("/")[0].strip()
                matched_opt = None
                for i in range(opts.count()):
                    opt_txt = opts.nth(i).inner_text().strip()
                    if prefix.lower() in opt_txt.lower():
                        matched_opt = opts.nth(i)
                        print(f"  ✓ Selected option (prefix match): {opt_txt}")
                        break
                if not matched_opt:
                    matched_opt = opts.first
                    print(f"  ✓ Selected option: {opts.first.inner_text().strip()}")
                matched_opt.click(force=True)
                time.sleep(1)

    # 2. Clean empty rows after filling
    clean_empty_genre_rows()

    print("✨ Genres Page populated cleanly (Save button not clicked as instructed)!")
