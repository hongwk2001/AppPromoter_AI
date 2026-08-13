"""
update_ckeditor_korean.py
Updates the CKEditor 5 Ebook Description box on D2D Step 2 with clean Korean text.
"""

import os
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OVERVIEW_PATH = os.path.join(BASE_DIR, "tono_bungay", "overview_ko.txt")

def update_ckeditor():
    with open(OVERVIEW_PATH, "r", encoding="utf-8") as f:
        overview_ko = f.read().strip()

    print(f"Reading Korean Description ({len(overview_ko)} chars):")
    print(overview_ko[:120] + "...\n")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]

        # Target CKEditor 5 editable div
        ck_editor = page.locator(".ck-editor__editable")
        if ck_editor.count() > 0:
            print("Found CKEditor 5 element (.ck-editor__editable)")
            ck_editor.first.click()
            page.wait_for_timeout(300)

            # Set content via JS evaluate formatting paragraphs into HTML
            paragraphs = overview_ko.split("\n\n")
            html_content = "".join([f"<p>{p.strip().replace(chr(10), '<br>')}</p>" for p in paragraphs if p.strip()])

            js_set = """
            (html) => {
                const el = document.querySelector('.ck-editor__editable');
                if (el) {
                    el.innerHTML = html;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    return el.innerText.substring(0, 150);
                }
                return 'Not found';
            }
            """
            result_text = page.evaluate(js_set, html_content)
            print("  ✓ Updated CKEditor inner text:")
            print(f"    {result_text}")
        else:
            print("  ⚠️ CKEditor editable element not found.")

        page.wait_for_timeout(800)

if __name__ == "__main__":
    update_ckeditor()
