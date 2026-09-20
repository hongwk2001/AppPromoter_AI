import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def test_label_fc():
    payload_path = os.path.join(NOTES_DIR, "ar_payload_blue_castle_ko.json")
    with open(payload_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    cover_path = payload.get("cover_path")
    print(f"Cover Path: {cover_path}")

    cdp_url = "http://127.0.0.1:9222"
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0]
        page = None
        for page_obj in context.pages:
            if "authorsrepublic.com" in page_obj.url:
                page = page_obj
                break
        if not page:
            page = context.pages[0]

        print(f"URL: {page.url}")

        print("Clicking .cover-select label with expect_file_chooser...")
        with page.expect_file_chooser(timeout=5000) as fc_info:
            page.click(".cover-select label")
        file_chooser = fc_info.value
        print(f"File chooser intercepted! Setting files to {cover_path}...")
        file_chooser.set_files(cover_path)

        time.sleep(3.0)

        has_cover = page.evaluate("""() => {
            const selectDiv = document.querySelector('.cover-select');
            const img = document.querySelector('#square-cover-wrapper img, .cover-image img, img[id*="cover"]');
            const wrapper = document.querySelector('#square-cover-wrapper');
            return {
                data_has_cover: selectDiv ? selectDiv.getAttribute('data-has-cover') : 'Unknown',
                img_src: img ? img.src : 'None',
                wrapper_html: wrapper ? wrapper.innerHTML : ''
            };
        }""")

        print(f"Result: data-has-cover = {has_cover['data_has_cover']}")
        print(f"Wrapper HTML: {has_cover['wrapper_html']}")

if __name__ == "__main__":
    test_label_fc()
