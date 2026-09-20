import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def trigger_cover():
    payload_path = os.path.join(NOTES_DIR, "ar_payload_blue_castle_ko.json")
    with open(payload_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    cover_path = payload.get("cover_path")
    print(f"Cover Image Path: {cover_path}")

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

        print("Setting input files and dispatching change event on #square-cover-file...")
        page.set_input_files("#square-cover-file", cover_path)
        page.evaluate("""() => {
            const input = document.querySelector('#square-cover-file');
            if (input) {
                input.dispatchEvent(new Event('change', { bubbles: true }));
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""")
        time.sleep(3.0)

        has_cover = page.evaluate("""() => {
            const selectDiv = document.querySelector('.cover-select');
            return selectDiv ? selectDiv.getAttribute('data-has-cover') : 'Unknown';
        }""")

        print(f"Cover Upload Status (data-has-cover): {has_cover}")

if __name__ == "__main__":
    trigger_cover()
