"""
d2d_1_fill_metadata.py
Populates Step 1 (Metadata & Cover Upload) on active Draft2Digital page over CDP port 9222.
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

def fill_step1(book_name, lang="ko", port=9222):
    data = load_unified_metadata(book_name, lang)
    if not data:
        print("Error: Could not load metadata.")
        return

    step1 = data["step1_metadata"]
    print(f"\n📋 Filling Step 1 (Metadata) for: {step1['title']} ({lang.upper()})")
    print(f"  Author:     {step1['author']}")
    print(f"  Publisher:  {step1['publisher']}")
    print(f"  Language:   {data['language_name']}\n")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "/book/" in pg.url]
        page = pages[0] if pages else [pg for pg in browser.contexts[0].pages if "draft2digital.com" in pg.url][0]
        print(f"Active Tab: {page.url} ({page.title()})")

        # 1. Fill Title
        if page.locator("#title").count() > 0:
            page.locator("#title").fill(step1["title"])
            print(f"  ✓ Filled Title (#title): {step1['title']}")

        # 2. Select Publisher
        pub_wrapper = page.locator("#publisher-field-wrapper")
        if pub_wrapper.count() > 0:
            curr_pub = pub_wrapper.inner_text()
            if step1["publisher"] not in curr_pub:
                page.locator("#publisher").click()
                page.wait_for_timeout(600)
                pub_opt = page.locator(f"text='{step1['publisher']}'")
                if pub_opt.count() > 0:
                    pub_opt.first.click()
                    print(f"  ✓ Selected Publisher: {step1['publisher']}")

        # 3. Fill / Select Author
        author_wrapper = page.locator("#authorName-field-wrapper")
        if author_wrapper.count() > 0:
            if step1["author"] not in author_wrapper.inner_text():
                page.locator("#authorName").click()
                page.wait_for_timeout(800)
                existing_author = page.locator(f"text='{step1['author']}'")
                if existing_author.count() > 0:
                    existing_author.first.click()
                    print(f"  ✓ Selected Author: {step1['author']}")
                else:
                    add_new = page.locator("text='Add New Author'")
                    if add_new.count() > 0:
                        add_new.first.click()
                        page.wait_for_timeout(600)
                        modal_inp = page.locator('.modal-content input, .modal-body input, div.modal input, #new-contributor').first
                        if modal_inp.count() > 0:
                            modal_inp.fill(step1["author"])
                            modal_btn = page.locator('.modal-content button, .modal-body button, div.modal button').first
                            if modal_btn.count() > 0:
                                modal_btn.click()
                            print(f"  ✓ Added Author via modal: {step1['author']}")
                        try:
                            page.wait_for_selector(".modal-backdrop", state="detached", timeout=5000)
                        except Exception:
                            pass
                page.wait_for_timeout(600)

        # 4. Select Language
        lang_wrapper = page.locator("#language-field-wrapper")
        if lang_wrapper.count() > 0:
            if data["language_name"] not in lang_wrapper.inner_text():
                page.locator("#language").click()
                page.wait_for_timeout(600)
                lang_opt = page.locator(f'#language-listbox div:has-text("{data["language_name"]}")')
                if lang_opt.count() > 0:
                    lang_opt.first.click()
                    print(f"  ✓ Selected Language: {data['language_name']}")

        # 5. Content Rating
        if not step1.get("explicit_content", False):
            general_label = page.locator("label:has-text('does NOT contain content inappropriate for minors')")
            if general_label.count() > 0:
                try:
                    general_label.first.click()
                    print("  ✓ Selected Content Rating: General Audience")
                except Exception:
                    pass

        # 6. Search Terms
        search_input = page.locator("#searchTerms")
        if search_input.count() > 0 and step1.get("search_terms"):
            for kw in step1["search_terms"]:
                search_input.fill("")
                search_input.type(kw, delay=50)
                search_input.press("Enter")
                page.wait_for_timeout(300)
            print(f"  ✓ Added {len(step1['search_terms'])} Search Terms")

        # 7. BISAC Categories
        if page.locator("#filter-bisacs").count() > 0 and step1.get("bisac_categories"):
            filter_input = page.locator("#filter-bisacs")
            for cat_path in step1["bisac_categories"]:
                leaf_name = cat_path.split("/")[-1].strip()
                filter_input.fill("")
                filter_input.type(leaf_name, delay=80)
                page.wait_for_timeout(500)

                js_click = """
                (leafName) => {
                    const leaves = Array.from(document.querySelectorAll('#bisac-list-wrapper .bisac-category'));
                    let match = leaves.find(el => el.innerText.trim() === leafName || (el.getAttribute('data-literal') || '').endsWith('/ ' + leafName));
                    if (match) { match.click(); return 'Clicked leaf'; }
                    const parent = leaves.find(el => el.innerText.includes('FICTION') || el.innerText.includes('POETRY'));
                    if (parent) { (parent.querySelector('i') || parent).click(); return 'Expanded parent'; }
                    return 'Not found';
                }
                """
                res = page.evaluate(js_click, leaf_name)
                page.wait_for_timeout(500)
                if "Expanded" in res:
                    page.evaluate(js_click, leaf_name)
                print(f"  ✓ Processed BISAC: {cat_path}")

        # 8. Upload Cover Image
        if step1.get("cover_exists") and step1.get("cover_image_path"):
            cover_radio = page.locator('#front-cover-upload-1, label:has-text("I have front cover art")')
            if cover_radio.count() > 0:
                try:
                    cover_radio.first.click()
                    page.wait_for_timeout(400)
                except Exception:
                    pass

            cover_input = page.locator('#upload-front-cover, input[type="file"][accept*="image"]')
            if cover_input.count() > 0:
                try:
                    cover_input.first.set_input_files(step1["cover_image_path"])
                    print(f"  ✓ Uploaded Cover Image: {os.path.basename(step1['cover_image_path'])}")
                except Exception as e:
                    print(f"  ⚠️ Cover upload warning: {e}")

        print("\n✨ Step 1 Autofill Finished! (Form populated — Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill Step 1 Form Fields & Pause for Review")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    fill_step1(args.book, args.lang, port=args.port)
