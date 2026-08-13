"""
fix_step2_korean_and_epub.py
Populates clean Korean descriptions and uploads manuscript EPUB for Tono-Bungay on D2D Step 2.
"""

import os
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TONO_DIR = os.path.join(BASE_DIR, "tono_bungay")

EPUB_PATH = os.path.join(TONO_DIR, "tono_bungay_ko.epub")
SHORT_DESC_PATH = os.path.join(TONO_DIR, "short_description_ko.txt")
OVERVIEW_PATH = os.path.join(TONO_DIR, "overview_ko.txt")

def fix_step2():
    with open(SHORT_DESC_PATH, "r", encoding="utf-8") as f:
        short_ko = f.read().strip()

    with open(OVERVIEW_PATH, "r", encoding="utf-8") as f:
        overview_ko = f.read().strip()

    print(f"🚀 Fixing Step 2 for Tono-Bungay (Korean Edition)...")
    print(f"  EPUB Path:   {EPUB_PATH} (Exists: {os.path.exists(EPUB_PATH)})")
    print(f"  Short Desc:  {short_ko[:60]}...")
    print(f"  Overview:    {overview_ko[:60]}...\n")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]

        # 1. Upload Manuscript EPUB (#ebook-upload-content)
        epub_input = page.locator('#ebook-upload-content, input[type="file"][accept*="epub"]')
        if epub_input.count() > 0:
            epub_input.first.set_input_files(EPUB_PATH)
            print("  ✓ Uploaded Manuscript EPUB: tono_bungay_ko.epub")
            page.wait_for_timeout(1000)

        # 2. Fill Short Description (#short-description-editor)
        if page.locator("#short-description-editor").count() > 0:
            page.locator("#short-description-editor").fill(short_ko)
            print("  ✓ Updated Short Description to Korean!")

        # 3. Fill Main Ebook Description in Rich Text Editor
        cq_editor = page.locator('.cq-editor, [contenteditable="true"]')
        if cq_editor.count() > 0:
            cq_editor.first.click()
            page.evaluate("""(text) => {
                const ed = document.querySelector('.cq-editor, [contenteditable="true"]');
                if (ed) {
                    ed.innerText = text;
                    ed.dispatchEvent(new Event('input', { bubbles: true }));
                    ed.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", overview_ko)
            print("  ✓ Updated Main Ebook Description to Korean!")

        page.wait_for_timeout(1000)
        print("\n✨ Step 2 Korean content & EPUB file successfully updated!")

if __name__ == "__main__":
    fix_step2()
