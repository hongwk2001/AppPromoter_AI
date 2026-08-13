"""
automate_d2d_step2.py
Automates Draft2Digital Step 2 (Ebook Details):
Uploads manuscript EPUB (#ebook-upload-content), populates Short Description & Full Description,
adds Non-Author Contributors (TKPROF LLC as Translator & Editor), and selects Free D2D ISBN.
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

def load_payload(book_name, lang="ko"):
    payload_file = os.path.join(NOTES_DIR, f"d2d_payload_{book_name}_{lang}.json")
    if not os.path.exists(payload_file):
        print(f"Payload file not found. Running prepare_d2d_metadata.py...")
        from prepare_d2d_metadata import prepare_payload
        return prepare_payload(book_name, lang)
    with open(payload_file, "r", encoding="utf-8") as f:
        return json.load(f)

def run_step2_autofill(book_name, lang="ko", port=9222):
    payload = load_payload(book_name, lang)
    if not payload:
        print("Error: Could not load book metadata payload.")
        return

    print(f"\n🚀 Initiating Draft2Digital Step 2 (Ebook Details) Autofill for: {payload['title']} ({lang.upper()})")
    print(f"  EPUB File: {payload['epub_path']}\n")

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

        # 1. Upload Manuscript EPUB (#ebook-upload-content)
        if payload["files_exist"]["epub"]:
            epub_input = page.locator('#ebook-upload-content, input[type="file"][accept*="epub"]')
            if epub_input.count() > 0:
                try:
                    epub_input.first.set_input_files(payload["epub_path"])
                    print(f"  ✓ Uploaded Manuscript EPUB (#ebook-upload-content): {os.path.basename(payload['epub_path'])}")
                except Exception as e:
                    print(f"  ⚠️ Could not set EPUB file directly: {e}")

        # 2. Fill Short Description (#short-description-editor)
        short_desc_path = os.path.join(BASE_DIR, book_name, f"short_description_{lang}.txt")
        short_text = ""
        if os.path.exists(short_desc_path):
            with open(short_desc_path, "r", encoding="utf-8") as f:
                short_text = f.read().strip()
        
        if not short_text and payload.get("description"):
            first_p = [p.strip() for p in payload["description"].split("\n\n") if p.strip() and not p.startswith("#")]
            short_text = first_p[0] if first_p else payload["description"][:300]
        
        if short_text and page.locator("#short-description-editor").count() > 0:
            page.locator("#short-description-editor").fill(short_text[:400])
            print("  ✓ Filled Short Description (#short-description-editor)")

        # 3. Fill Ebook Description in CKEditor 5 (.ck-editor__editable)
        if payload.get("description"):
            desc_text = payload["description"]
            ck_editor = page.locator(".ck-editor__editable, .cq-editor, [contenteditable='true']")
            if ck_editor.count() > 0:
                try:
                    ck_editor.first.click()
                    page.wait_for_timeout(300)
                    
                    paragraphs = desc_text.split("\n\n")
                    html_content = "".join([f"<p>{p.strip().replace(chr(10), '<br>')}</p>" for p in paragraphs if p.strip()])
                    
                    js_fill = """
                    (htmlText) => {
                        const el = document.querySelector('.ck-editor__editable');
                        if (el && el.ckeditorInstance) {
                            el.ckeditorInstance.setData(htmlText);
                            return 'setData success';
                        }
                        if (el) {
                            el.innerHTML = htmlText;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                            el.dispatchEvent(new Event('blur', { bubbles: true }));
                            return 'innerHTML fallback';
                        }
                        return 'el not found';
                    }
                    """
                    res = page.evaluate(js_fill, html_content)
                    print(f"  ✓ Filled Ebook Description in CKEditor 5 ({res})")
                except Exception as e:
                    print(f"  ⚠️ Could not fill rich text editor: {e}")

        # 4. Add Non-Author Contributors (TKPROF LLC as Translator & Editor)
        print("\nAdding Non-Author Contributors (TKPROF LLC)...")
        contributor_wrapper = page.locator("#contributors-field-wrapper")
        if contributor_wrapper.count() > 0:
            # Expand contributor section if button exists
            add_contrib_btn = contributor_wrapper.locator('button:has-text("ADD NON-AUTHOR CONTRIBUTORS")')
            if add_contrib_btn.count() > 0 and add_contrib_btn.is_visible():
                add_contrib_btn.click()
                page.wait_for_timeout(600)

            roles = ["Translator", "Editor"]
            curr_text = contributor_wrapper.inner_text()

            for role_name in roles:
                if f"TKPROF LLC" in curr_text and role_name in curr_text:
                    print(f"  ✓ Contributor TKPROF LLC ({role_name}) already present.")
                    continue

                print(f"  Adding TKPROF LLC as {role_name}...")
                # 4a. Select Name (#newContributorName)
                if page.locator("#newContributorName").count() > 0:
                    page.locator("#newContributorName").click()
                    page.wait_for_timeout(600)
                    
                    tkprof_opt = page.locator("text='TKPROF LLC'")
                    if tkprof_opt.count() > 0:
                        tkprof_opt.first.click()
                        print("    ✓ Selected name: TKPROF LLC")
                    else:
                        add_new = page.locator("text='Add New Author', text='Add New'")
                        if add_new.count() > 0:
                            add_new.first.click()
                            page.wait_for_timeout(600)
                            inp = page.locator("#new-contributor")
                            if inp.count() > 0:
                                inp.fill("TKPROF LLC")
                                modal_btn = page.locator(".modal-body button")
                                if modal_btn.count() > 0:
                                    modal_btn.first.click()
                                    page.wait_for_timeout(600)
                                print("    ✓ Added name: TKPROF LLC")

                # 4b. Select Role (#newContributorRole)
                if page.locator("#newContributorRole").count() > 0:
                    page.locator("#newContributorRole").click()
                    page.wait_for_timeout(600)
                    
                    role_opt = page.locator(f"text='{role_name}'")
                    if role_opt.count() > 0:
                        role_opt.first.click()
                        print(f"    ✓ Selected role: {role_name}")
                    else:
                        print(f"    ⚠️ Role '{role_name}' not found.")

                # 4c. Click Add (+) button
                add_btn = page.locator('#contributors-field-wrapper button:has-text("+"), #contributors-field-wrapper i.fa-plus, #contributors-field-wrapper button')
                if add_btn.count() > 0:
                    try:
                        add_btn.first.click()
                        print(f"    ✓ Added contributor: TKPROF LLC ({role_name})")
                        page.wait_for_timeout(800)
                    except Exception as e:
                        print(f"    ⚠️ Could not click Add button: {e}")

        # 5. Free Draft2Digital ISBN Radio Selection
        free_isbn_radio = page.locator('label:has-text("Give me a free Draft2Digital ISBN"), input[value*="free"]')
        if free_isbn_radio.count() > 0:
            try:
                free_isbn_radio.first.click()
                print("\n  ✓ Selected: Give me a free Draft2Digital ISBN")
            except Exception:
                pass

        print("\n✨ Draft2Digital Step 2 Autofill Completed Successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate Draft2Digital Step 2 Ebook Details")
    parser.add_argument("--book", type=str, required=True, help="Book folder name (e.g. the_enchanted_april, secret_garden, gilgamesh, tono_bungay)")
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"], help="Language edition (ko or en)")
    parser.add_argument("--port", type=int, default=9222, help="Chrome CDP port (default: 9222)")
    args = parser.parse_args()

    run_step2_autofill(args.book, args.lang, port=args.port)
