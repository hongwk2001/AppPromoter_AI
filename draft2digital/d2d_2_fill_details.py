"""
d2d_2_fill_details.py
Populates Step 2 (Ebook Details, Manuscript EPUB, Descriptions, Contributors, ISBN)
on active Draft2Digital page over CDP port 9222.
STOPS immediately after filling for user review — does NOT click Save & Continue or move to next page.
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

def fill_step2(book_name, lang="ko", port=9222):
    data = load_unified_metadata(book_name, lang)
    if not data:
        print("Error: Could not load metadata.")
        return

    step2 = data["step2_details"]
    print(f"\n📋 Filling Step 2 (Ebook Details) for: {data['step1_metadata']['title']} ({lang.upper()})")
    print(f"  EPUB File: {step2['epub_path']}\n")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "/book/" in pg.url]
        page = pages[0] if pages else [pg for pg in browser.contexts[0].pages if "draft2digital.com" in pg.url][0]
        print(f"Active Tab: {page.url} ({page.title()})")

        # 1. Upload Manuscript EPUB
        if step2.get("epub_exists") and step2.get("epub_path"):
            epub_input = page.locator('#ebook-upload-content, input[type="file"][accept*="epub"]')
            if epub_input.count() > 0:
                try:
                    epub_input.first.set_input_files(step2["epub_path"])
                    print(f"  ✓ Uploaded Manuscript EPUB: {os.path.basename(step2['epub_path'])}")
                except Exception as e:
                    print(f"  ⚠️ EPUB upload warning: {e}")

        # 2. Fill Short Description
        if step2.get("short_description") and page.locator("#short-description-editor").count() > 0:
            page.locator("#short-description-editor").fill(step2["short_description"][:400])
            print("  ✓ Filled Short Description (#short-description-editor)")

        # 3. Fill CKEditor 5 Full Description
        if step2.get("full_description_text"):
            desc_text = step2["full_description_text"]
            ck_editor = page.locator(".ck-editor__editable, [contenteditable='true']")
            if ck_editor.count() > 0:
                try:
                    ck_editor.first.click()
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
                            return 'innerHTML fallback';
                        }
                        return 'el not found';
                    }
                    """
                    res = page.evaluate(js_fill, html_content)
                    print(f"  ✓ Filled CKEditor 5 Description ({res})")
                except Exception as e:
                    print(f"  ⚠️ CKEditor fill warning: {e}")

        # 4. Add Contributors
        contributor_wrapper = page.locator("#contributors-field-wrapper")
        if contributor_wrapper.count() > 0 and step2.get("contributors"):
            add_contrib_btn = contributor_wrapper.locator('button:has-text("ADD NON-AUTHOR CONTRIBUTORS")')
            if add_contrib_btn.count() > 0 and add_contrib_btn.is_visible():
                add_contrib_btn.click()
                page.wait_for_timeout(500)

            for contrib in step2["contributors"]:
                c_name = contrib["name"]
                c_role = contrib["role"]
                curr_text = contributor_wrapper.inner_text()
                if c_name in curr_text and c_role in curr_text:
                    print(f"  ✓ Contributor {c_name} ({c_role}) already present.")
                    continue

                if page.locator("#newContributorName").count() > 0:
                    page.locator("#newContributorName").click()
                    page.wait_for_timeout(400)
                    name_opt = page.locator(f"text='{c_name}'")
                    if name_opt.count() > 0:
                        name_opt.first.click()

                if page.locator("#newContributorRole").count() > 0:
                    page.locator("#newContributorRole").click()
                    page.wait_for_timeout(400)
                    role_opt = page.locator(f"text='{c_role}'")
                    if role_opt.count() > 0:
                        role_opt.first.click()

                add_btn = page.locator('#contributors-field-wrapper button:has-text("+"), #contributors-field-wrapper button')
                if add_btn.count() > 0:
                    try:
                        add_btn.first.click()
                        print(f"  ✓ Added Contributor: {c_name} ({c_role})")
                        page.wait_for_timeout(600)
                    except Exception:
                        pass

            # Reset/Clear pending contributor dropdown row if needed so Save & Continue is enabled
            if "Finish adding" in contributor_wrapper.inner_text() or page.locator("#newContributorName").count() > 0:
                if page.locator("#newContributorRole").count() > 0:
                    page.locator("#newContributorRole").click()
                    page.wait_for_timeout(300)
                    none_role = page.locator("text='(none)'")
                    if none_role.count() > 0:
                        none_role.first.click()
                if page.locator("#newContributorName").count() > 0:
                    page.locator("#newContributorName").click()
                    page.wait_for_timeout(300)
                    none_opt = page.locator("text='(none)'")
                    if none_opt.count() > 0:
                        none_opt.first.click()
                    print("  ✓ Cleared pending contributor dropdown with (none)")
                    page.wait_for_timeout(400)

        # 5. Free Draft2Digital ISBN Radio Selection
        if step2.get("use_free_d2d_isbn", True):
            free_isbn_radio = page.locator('label:has-text("Give me a free Draft2Digital ISBN"), input[value*="free"]')
            if free_isbn_radio.count() > 0:
                try:
                    free_isbn_radio.first.click()
                    print("  ✓ Selected: Free Draft2Digital ISBN")
                except Exception:
                    pass

        print("\n✨ Step 2 Autofill Finished! (Form populated — Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill Step 2 Form Fields & Pause for Review")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    fill_step2(args.book, args.lang, port=args.port)
