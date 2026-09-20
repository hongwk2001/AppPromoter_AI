import time
import os
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_upload():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "content" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        cover_path = r"C:\git_repo\TKprof_book\books\blue_castle\cover_ko.jpg"

        # Check if button with xapuploadertrigger exists inside open dialog
        browse_btn = page.locator('button[xapuploadertrigger], button:has-text("Browse")').first
        if browse_btn.count() > 0:
            print("Found browse button:", browse_btn.evaluate("el => el.outerHTML"))

            # Register filechooser event before clicking
            print("Attaching filechooser event listener...")
            with page.expect_file_chooser(timeout=5000) as fc_info:
                browse_btn.click(force=True)
            
            file_chooser = fc_info.value
            print("✓ FileChooser triggered! Setting cover_ko.jpg...")
            file_chooser.set_files(cover_path)
            print("✅ Set cover_ko.jpg successfully!")

if __name__ == "__main__":
    test_upload()
