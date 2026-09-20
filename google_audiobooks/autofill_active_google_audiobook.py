import os
import sys
import time
import json
import argparse
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def load_google_metadata(book_name="gilgamesh", lang="ko"):
    meta_path = os.path.join(NOTES_DIR, f"google_audio_metadata_{book_name}_{lang}.json")
    if not os.path.exists(meta_path):
        print(f"Metadata file not found: {meta_path}. Running prepare_metadata script...")
        from google_audio_0_prepare_metadata import prepare_audiobook_metadata
        return prepare_audiobook_metadata(book_name, lang)
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def autofill_active_google(book_name="gilgamesh", lang="ko", port=9222):
    meta = load_google_metadata(book_name, lang)
    book_info = meta.get("book_info", {})
    cf = meta.get("content_files", {})
    contributors = meta.get("contributors", [])

    cover_path = cf.get("cover_image_path")
    audio_files = cf.get("audio_files", [])
    all_files = [cover_path] + audio_files if cover_path else audio_files

    print(f"\n🚀 Initiating Google Books Autofill for Active Open Tab")
    print(f"  Title:      {book_info.get('title')}")
    print(f"  Language:   {meta.get('language_name')} ({lang})")
    print(f"  Files:      Cover + {len(audio_files)} MP3 audio tracks\n")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"❌ Error connecting to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        print(f"Active Page URL: {page.url}")

        base_hash = page.url.split("#")[0]
        fragment = page.url.split("#")[1] if "#" in page.url else ""
        book_id = fragment.split(";")[0] if fragment else ""

        if not book_id:
            print("❌ Active page URL does not contain a book ID fragment (#book/GGKEY:...).")
            return

        book_base_url = f"{base_hash}#{book_id};jc=true"

        # ---------------------------------------------------------------------
        # 1. Content & Cover Upload
        # ---------------------------------------------------------------------
        content_url = f"{book_base_url}/content"
        print(f"\n--- [1/4] Content & Cover Upload: {content_url} ---")
        page.goto(content_url)
        time.sleep(2.5)

        upload_btn = page.locator('button:has-text("Upload files"), [role="button"]:has-text("Upload files"), button:has-text("Upload a cover")').first
        if upload_btn.count() > 0 and upload_btn.is_visible():
            print("➡️ Clicking Upload files trigger...")
            upload_btn.click(force=True)
            time.sleep(1.5)

        client = page.context.new_cdp_session(page)
        client.send("DOM.enable")
        doc = client.send("DOM.getDocument")
        node = client.send("DOM.querySelector", {
            "nodeId": doc["root"]["nodeId"],
            "selector": 'input[type="file"]'
        })
        node_id = node.get("nodeId")

        if node_id and node_id > 0:
            print(f"➡️ Injecting {len(all_files)} files via native CDP Protocol...")
            client.send("DOM.setFileInputFiles", {
                "files": all_files,
                "nodeId": node_id
            })
            time.sleep(2.0)
            print("  ✓ CDP setFileInputFiles complete!")

        # ---------------------------------------------------------------------
        # 2. Book Info (About, Genres, Contributors)
        # ---------------------------------------------------------------------
        about_url = f"{book_base_url}/info/about"
        print(f"\n--- [2/4] Book Info (About): {about_url} ---")
        page.goto(about_url)
        time.sleep(2.5)

        # Title & Subtitle (Use exact element index targeting)
        sub_btn = page.locator('button:has-text("Add a subtitle"), [role="button"]:has-text("Add a subtitle"), a:has-text("Add a subtitle")').first
        if sub_btn.count() > 0 and sub_btn.is_visible():
            sub_btn.click(force=True)
            time.sleep(0.8)

        inps = page.locator('input.mat-mdc-input-element')
        if inps.count() >= 1 and book_info.get('title'):
            print(f"➡️ Setting Title (input [0]): {book_info.get('title')}")
            inps.nth(0).click(force=True)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            inps.nth(0).fill(book_info.get('title'))
            time.sleep(0.5)

        if inps.count() >= 2 and book_info.get('subtitle'):
            print(f"➡️ Setting Subtitle (input [1]): {book_info.get('subtitle')}")
            inps.nth(1).click(force=True)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            inps.nth(1).fill(book_info.get('subtitle'))
            time.sleep(0.5)

        # Duration
        dur_inp = page.locator('mat-form-field:has-text("Duration") input, input[placeholder*="HH:MM:SS" i]').first
        if dur_inp.count() > 0 and book_info.get('duration'):
            print(f"➡️ Setting Duration: {book_info.get('duration')}")
            dur_inp.click(force=True)
            dur_inp.fill(book_info.get('duration'))
            time.sleep(0.5)

        # Description
        desc_editor = page.locator('.ql-editor, textarea[aria-label*="Description" i]').first
        if desc_editor.count() > 0 and book_info.get('description'):
            print("➡️ Filling HTML Description...")
            desc_editor.click(force=True)
            desc_editor.fill(book_info.get('description'))
            time.sleep(0.5)

        # Save About
        print("  ✓ About fields populated (Save button not clicked as instructed).")

        # Genres
        genres_url = f"{book_base_url}/info/genres"
        print(f"\n--- [3/4] Genres: {genres_url} ---")
        if "info/genres" not in page.url:
            page.goto(genres_url)
            time.sleep(2)

        # Clean existing chips if any
        remove_btns = page.locator('mat-chip-row button[aria-label*="Remove" i], mat-chip-row button:has-text("close")')
        for i in range(remove_btns.count()):
            try:
                remove_btns.nth(i).click(force=True)
                time.sleep(0.3)
            except Exception:
                pass

        categories = book_info.get('categories', ["소설", "FICTION / Classics"])
        for cat in categories:
            add_btn = page.locator('button:has-text("Add a genre"), [role="button"]:has-text("Add a genre")').first
            if add_btn.count() > 0 and add_btn.is_visible():
                add_btn.click(force=True)
                time.sleep(1)

            # For Korean, select GKSS (Korean) scheme in mat-select
            if lang == "ko":
                sel = page.locator('mat-select').last
                if sel.count() > 0 and "GKSS" not in sel.inner_text():
                    sel.click(force=True)
                    time.sleep(0.5)
                    opt = page.locator('mat-option:has-text("GKSS")').first
                    if opt.count() > 0:
                        opt.click(force=True)
                        time.sleep(0.5)

            inp = page.locator('mat-form-field input, input[placeholder*="Genre" i]').last
            if inp.count() > 0:
                query = cat.split("/")[-1].strip()
                print(f"➡️ Adding Genre query: {query}")
                inp.click(force=True)
                inp.fill(query)
                time.sleep(1.5)

                opts = page.locator('mat-option')
                if opts.count() > 0:
                    first_opt = opts.first.inner_text().strip()
                    print(f"  ✓ Selected option: {first_opt}")
                    opts.first.click(force=True)
                    time.sleep(1)

        # Clean empty genre rows
        page.evaluate("""() => {
            const rows = Array.from(document.querySelectorAll('mat-form-field')).filter(ff => {
                const inp = ff.querySelector('input');
                return inp && inp.value.trim() === '';
            });
            rows.forEach(r => {
                const btn = r.parentElement ? r.parentElement.querySelector('button') : null;
                if (btn) btn.click();
            });
        }""")
        time.sleep(1.0)
        print("  ✓ Genres fields populated (Save button not clicked as instructed).")

        # Contributors
        contrib_url = f"{book_base_url}/info/contributors"
        print(f"\n--- [4/4] Contributors: {contrib_url} ---")
        if "info/contributors" not in page.url:
            page.goto(contrib_url)
            time.sleep(2)

        for idx, contrib in enumerate(contributors):
            name = contrib.get("name")
            role = contrib.get("role")

            name_inps = page.locator('mat-form-field:has-text("Name") input, input[placeholder*="Name" i]')
            if name_inps.count() <= idx:
                add_btn = page.locator('button:has-text("Add a contributor")').first
                if add_btn.count() > 0 and add_btn.is_visible():
                    add_btn.click(force=True)
                    time.sleep(1)

            name_inps = page.locator('mat-form-field:has-text("Name") input, input[placeholder*="Name" i]')
            if name_inps.count() > idx:
                print(f"➡️ Contributor [{idx+1}] Name: {name}")
                name_inps.nth(idx).click(force=True)
                name_inps.nth(idx).fill(name)
                time.sleep(0.5)

            role_sel = page.locator('mat-form-field:has-text("Role") mat-select, mat-select')
            if role_sel.count() > idx:
                print(f"➡️ Contributor [{idx+1}] Role: {role}")
                role_sel.nth(idx).click(force=True)
                time.sleep(0.5)
                opt = page.locator(f'mat-option:has-text("{role}")').first
                if opt.count() > 0:
                    opt.click(force=True)
                    time.sleep(0.5)

        print("  ✓ Contributors fields populated (Save button not clicked as instructed).")

        # ---------------------------------------------------------------------
        # 3. Pricing
        # ---------------------------------------------------------------------
        pricing_url = f"{book_base_url}/pricing"
        print(f"\n--- Pricing: {pricing_url} ---")
        page.goto(pricing_url)
        time.sleep(2.5)

        price_inp = page.locator('input[aria-label*="Price" i], input[placeholder*="Price" i], mat-form-field:has-text("Price") input').first
        if price_inp.count() > 0:
            print("➡️ Setting Price: 9.99")
            price_inp.click(force=True)
            price_inp.fill("9.99")
            time.sleep(0.5)

        print("  ✓ Pricing fields populated (Save button not clicked as instructed).")

        print(f"\n🎉 Google Books Autofill for '{book_info.get('title')}' complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", default="gilgamesh")
    parser.add_argument("--lang", default="ko")
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    autofill_active_google(args.book, args.lang, args.port)
