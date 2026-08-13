"""
automate_d2d_upload.py
Connects to an open Chrome session on http://127.0.0.1:9222,
populates the Draft2Digital book entry form with metadata (Title, Author, Publisher, Language, Search Terms with Enter key, BISAC Categories, Content Rating)
and attaches cover image (#upload-front-cover) and manuscript file.
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

def run_d2d_autofill(book_name, lang="ko", port=9222):
    payload = load_payload(book_name, lang)
    if not payload:
        print("Error: Could not load book metadata payload.")
        return

    print(f"\n🚀 Initiating Draft2Digital Autofill for: {payload['title']} ({lang.upper()})")
    print(f"  Author:           {payload['author']}")
    print(f"  Publisher:        {payload['publisher']}")
    print(f"  Language:         {payload.get('language', 'Korean')}")
    print(f"  Content Rating:   General Audience (explicit_content={payload['explicit_content']})")
    print(f"  Categories:       {payload.get('categories', [])}")
    print(f"  EPUB File:        {payload['epub_path']}")
    print(f"  Cover Image:      {payload['cover_path']}\n")

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

        # 1. Fill Book Title (#title)
        if page.locator("#title").count() > 0:
            page.locator("#title").fill(payload["title"])
            print(f"  ✓ Filled Title (#title): {payload['title']}")

        # 2. Fill / Select Publisher (#publisher)
        pub_wrapper = page.locator("#publisher-field-wrapper")
        if pub_wrapper.count() > 0:
            curr_pub = pub_wrapper.inner_text()
            target_pub = payload.get("publisher", "TKPROF LLC")
            if target_pub not in curr_pub:
                page.locator("#publisher").click()
                page.wait_for_timeout(600)
                pub_opt = page.locator(f"text='{target_pub}'")
                if pub_opt.count() > 0:
                    pub_opt.first.click()
                    print(f"  ✓ Selected Publisher: {target_pub}")
                else:
                    print(f"  ⚠️ Publisher option '{target_pub}' not found.")
            else:
                print(f"  ✓ Publisher already set to: {target_pub}")

        # 3. Fill / Select Author Name (#authorName)
        author_wrapper = page.locator("#authorName-field-wrapper")
        if author_wrapper.count() > 0:
            target_author = payload.get("author")
            if not target_author or target_author == "TKPROF LLC":
                target_author = "Anonymous" if lang == "en" else "작자 미상"
            
            curr_author_text = author_wrapper.inner_text()
            # Replace if author text contains personal names or doesn't match target_author
            if target_author not in curr_author_text or "Hong" in curr_author_text or "Billy" in curr_author_text or "TKPROF" in curr_author_text:
                page.locator("#authorName").click()
                page.wait_for_timeout(800)
                existing_author = page.locator(f"text='{target_author}'")
                if existing_author.count() > 0:
                    existing_author.first.click()
                    print(f"  ✓ Selected Author: {target_author}")
                else:
                    add_new = page.locator("text='Add New Author'")
                    if add_new.count() > 0:
                        add_new.first.click()
                        page.wait_for_timeout(600)
                        author_input = page.locator('#new-contributor, input[placeholder*="Author"], input[type="text"]').last
                        if author_input.count() > 0:
                            author_input.fill(target_author)
                            modal_btn = page.locator(".modal-body button")
                            if modal_btn.count() > 0:
                                modal_btn.first.click()
                                page.wait_for_timeout(600)
                            print(f"  ✓ Added & Filled Author: {target_author}")
            else:
                print(f"  ✓ Author correctly set to: {target_author}")

        # 4. Fill / Select Language (#language)
        lang_wrapper = page.locator("#language-field-wrapper")
        if lang_wrapper.count() > 0:
            target_lang = payload.get("language", "Korean")
            curr_lang_text = lang_wrapper.inner_text()
            if target_lang not in curr_lang_text:
                page.locator("#language").click()
                page.wait_for_timeout(600)
                lang_opt = page.locator(f'#language-listbox div:has-text("{target_lang}")')
                if lang_opt.count() == 0:
                    lang_opt = page.get_by_text(target_lang)
                if lang_opt.count() > 0:
                    lang_opt.first.click()
                    print(f"  ✓ Selected Language: {target_lang}")
                else:
                    print(f"  ⚠️ Language option '{target_lang}' not found.")
            else:
                print(f"  ✓ Language already set to: {target_lang}")

        # 5. Content Rating Selection (General Audience)
        if not payload.get("explicit_content", False):
            general_label = page.locator("label:has-text('does NOT contain content inappropriate for minors'), label:has-text('general audience')")
            if general_label.count() > 0:
                try:
                    general_label.first.click()
                    print("  ✓ Selected Content Rating: General Audience (NOT inappropriate for minors)")
                except Exception:
                    pass

        # 6. Fill Search Terms (#searchTerms) with Enter keypresses
        search_input = page.locator("#searchTerms")
        if search_input.count() > 0 and payload.get("keywords"):
            for kw in payload["keywords"]:
                search_input.fill("")
                search_input.type(kw, delay=50)
                search_input.press("Enter")
                page.wait_for_timeout(350)
            print(f"  ✓ Added {len(payload['keywords'])} Search Terms via Enter keypresses")

        # 7. BISAC Subject Category Selection (JS-assisted & Idempotent)
        if page.locator("#filter-bisacs").count() > 0 and payload.get("categories"):
            chosen_container = page.locator("#chosen-bisac-list, #prioritized-bisacs-wrapper").first
            
            # Remove any unwanted YOUNG ADULT items if present
            for _ in range(5):
                curr_chosen_text = chosen_container.inner_text()
                if "YOUNG ADULT" in curr_chosen_text:
                    del_btn = chosen_container.locator(".delete-item").first
                    if del_btn.count() > 0:
                        del_btn.click()
                        page.wait_for_timeout(300)
                else:
                    break

            filter_input = page.locator("#filter-bisacs")

            for cat_path in payload["categories"]:
                parts = [p.strip() for p in cat_path.split("/")]
                leaf_name = parts[-1]
                
                # Check if already present in chosen list
                curr_chosen_text = chosen_container.inner_text()
                if leaf_name in curr_chosen_text and "FICTION" in curr_chosen_text:
                    print(f"  ✓ Category already present in chosen list: {cat_path}")
                    continue

                filter_input.fill("")
                filter_input.type(leaf_name, delay=80)
                page.wait_for_timeout(600)

                js_click = """
                (leafName) => {
                    const leaves = Array.from(document.querySelectorAll('#bisac-list-wrapper .bisac-category'));
                    let match = leaves.find(el => el.innerText.trim() === leafName || el.getAttribute('data-literal').endsWith('/ ' + leafName));
                    if (match) {
                        match.click();
                        return 'Clicked leaf direct: ' + leafName;
                    }
                    
                    const parent = leaves.find(el => el.innerText.includes('FICTION') || el.innerText.includes('JUVENILE'));
                    if (parent) {
                        const icon = parent.querySelector('i');
                        if (icon) icon.click();
                        else parent.click();
                        return 'Expanded parent for: ' + leafName;
                    }
                    return 'Not found';
                }
                """
                res = page.evaluate(js_click, leaf_name)
                page.wait_for_timeout(600)
                
                if "Expanded" in res:
                    page.evaluate(js_click, leaf_name)
                    page.wait_for_timeout(600)

                print(f"  ✓ Processed BISAC Category: {cat_path}")

        # 8. Fill Description in CKEditor / Rich Text Editor
        if payload.get("description"):
            desc_text = payload["description"]
            editor = page.locator('.ck-editor__editable, .cq-editor, [contenteditable="true"]')
            if editor.count() > 0:
                try:
                    editor.first.click()
                    page.wait_for_timeout(300)
                    js_fill_desc = """
                    (text) => {
                        const el = document.querySelector('.ck-editor__editable, .cq-editor, [contenteditable="true"]');
                        if (!el) return 'Editor not found';
                        if (el.ckeditorInstance) {
                            el.ckeditorInstance.setData(text);
                            return 'Set via ckeditorInstance';
                        }
                        el.innerText = text;
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        el.dispatchEvent(new Event('blur', { bubbles: true }));
                        return 'Set via innerText and events';
                    }
                    """
                    res = page.evaluate(js_fill_desc, desc_text)
                    print(f"  ✓ Filled Description in Editor: ({len(desc_text)} chars) -> {res}")
                except Exception as e:
                    print(f"  ⚠️ Could not fill Description: {e}")

        # 9. Upload Cover Image (#upload-front-cover)
        if payload["files_exist"]["cover"]:
            have_cover_radio = page.locator('#front-cover-upload-1, label:has-text("I have front cover art")')
            if have_cover_radio.count() > 0:
                try:
                    have_cover_radio.first.click()
                    page.wait_for_timeout(500)
                except Exception:
                    pass

            cover_input = page.locator('#upload-front-cover, input[type="file"][accept*="image"]')
            if cover_input.count() > 0:
                try:
                    cover_input.first.set_input_files(payload["cover_path"])
                    print(f"  ✓ Uploaded Cover Image (#upload-front-cover): {os.path.basename(payload['cover_path'])}")
                except Exception as e:
                    print(f"  ⚠️ Could not set cover file directly: {e}")

        # 10. Upload Manuscript EPUB File (#ebook-upload-content / #upload-manuscript)
        if payload["files_exist"]["epub"]:
            epub_input = page.locator('#ebook-upload-content, #upload-manuscript, input[type="file"][accept*="epub"]')
            if epub_input.count() > 0:
                try:
                    epub_input.first.set_input_files(payload["epub_path"])
                    print(f"  ✓ Uploaded Manuscript EPUB: {os.path.basename(payload['epub_path'])}")
                    page.wait_for_timeout(1000)
                except Exception as e:
                    print(f"  ⚠️ Could not set manuscript EPUB file: {e}")

        print("\n✨ Draft2Digital Form Inspection & Autofill Completed Successfully!")
        print("🛑 Notice: 'Save & Continue' was NOT clicked (as instructed). Please review the filled page in your browser window.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate Draft2Digital Upload & Form Entry")
    parser.add_argument("--book", type=str, required=True, help="Book folder name (e.g. beowulf, the_enchanted_april, secret_garden, gilgamesh, tono_bungay)")
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"], help="Language edition (ko or en)")
    parser.add_argument("--port", type=int, default=9222, help="Chrome CDP port (default: 9222)")
    args = parser.parse_args()

    run_d2d_autofill(args.book, args.lang, port=args.port)
