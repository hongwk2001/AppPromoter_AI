import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def test_segment_uploads():
    payload_path = os.path.join(NOTES_DIR, "ar_payload_richest_man_in_babylon_en.json")
    with open(payload_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

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
            print("No page found")
            return

        print("\n--- Testing Explicit Segment ID Audio Uploads ---")

        # 1. Opening Track (data-segment-id="1")
        if payload.get('opening_track') and os.path.exists(payload['opening_track']):
            print(f"Setting Opening Track (segment 1): {payload['opening_track']}")
            page.set_input_files('input[data-segment-id="1"]', payload['opening_track'])
            page.evaluate("""() => {
                const el = document.querySelector('input[data-segment-id="1"]');
                if (el) {
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }""")
            time.sleep(3)

        # 2. Closing Track (data-segment-id="2")
        if payload.get('closing_track') and os.path.exists(payload['closing_track']):
            print(f"Setting Closing Track (segment 2): {payload['closing_track']}")
            page.set_input_files('input[data-segment-id="2"]', payload['closing_track'])
            page.evaluate("""() => {
                const el = document.querySelector('input[data-segment-id="2"]');
                if (el) {
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }""")
            time.sleep(3)

        # 3. Sample Track (data-segment-id="3")
        if payload.get('sample_track') and os.path.exists(payload['sample_track']):
            print(f"Setting Sample Track (segment 3): {payload['sample_track']}")
            page.set_input_files('input[data-segment-id="3"]', payload['sample_track'])
            page.evaluate("""() => {
                const el = document.querySelector('input[data-segment-id="3"]');
                if (el) {
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }""")
            time.sleep(3)

        # Check hidden status values after setting single tracks
        status = page.evaluate("""() => {
            return {
                opening: document.querySelector('#HasOpeningTrackHidden') ? document.querySelector('#HasOpeningTrackHidden').value : '',
                closing: document.querySelector('#HasClosingTrackHidden') ? document.querySelector('#HasClosingTrackHidden').value : '',
                sample: document.querySelector('#HasSampleTrackHidden') ? document.querySelector('#HasSampleTrackHidden').value : '',
                chapters: document.querySelector('#HasChapterTrackHidden') ? document.querySelector('#HasChapterTrackHidden').value : ''
            };
        }""")

        print(f"Status Flags after single track uploads: {json.dumps(status, indent=2)}")

if __name__ == "__main__":
    test_segment_uploads()
