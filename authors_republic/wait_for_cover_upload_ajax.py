import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def test_cover_ajax():
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

        print(f"Active Page: {page.url}")

        with page.expect_file_chooser(timeout=5000) as fc_info:
            page.click(".cover-select label")
        file_chooser = fc_info.value
        file_chooser.set_files(cover_path)
        print("File chooser submitted.")

        # Wait up to 15 seconds to monitor DOM updates
        print("Monitoring cover upload DOM updates...")
        for i in range(15):
            res = page.evaluate("""() => {
                const selectDiv = document.querySelector('.cover-select');
                const img = document.querySelector('#square-cover-wrapper img, .cover-image img');
                const bg = document.querySelector('#square-cover-wrapper') ? document.querySelector('#square-cover-wrapper').style.backgroundImage : '';
                return {
                    has_cover: selectDiv ? selectDiv.getAttribute('data-has-cover') : 'false',
                    img: img ? img.src : 'None',
                    bg: bg
                };
            }""")
            print(f" [{i+1}s] data-has-cover={res['has_cover']} | img={res['img']} | bg={res['bg']}")
            if res['has_cover'] == 'True' or res['img'] != 'None' or res['bg']:
                print("✅ Cover upload detected on page!")
                break
            time.sleep(1.0)

if __name__ == "__main__":
    test_cover_ajax()
