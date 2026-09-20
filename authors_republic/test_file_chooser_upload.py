import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def test_file_chooser():
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

        closing_file = payload['closing_track']
        sample_file = payload['sample_track']

        print(f"\n1. Uploading Closing Track via expect_file_chooser: {closing_file}")
        try:
            with page.expect_file_chooser(timeout=5000) as fc_info:
                page.evaluate("() => document.querySelector('input[data-segment-id=\"2\"]').parentElement.querySelector('label').click()")
            fc = fc_info.value
            fc.set_files(closing_file)
            print("  File chooser set for Closing Track. Waiting for upload...")
        except Exception as e:
            print(f"  File chooser error for closing: {e}")
            page.set_input_files('input[data-segment-id="2"]', closing_file)

        # Wait for closing flag
        for i in range(20):
            val = page.evaluate("() => document.querySelector('#HasClosingTrackHidden') ? document.querySelector('#HasClosingTrackHidden').value : ''")
            print(f"  [{i}s] HasClosingTrackHidden = {val}")
            if val == "True":
                print("✅ Closing Track confirmed!")
                break
            time.sleep(1)

        print(f"\n2. Uploading Sample Track via expect_file_chooser: {sample_file}")
        try:
            with page.expect_file_chooser(timeout=5000) as fc_info:
                page.evaluate("() => document.querySelector('input[data-segment-id=\"3\"]').parentElement.querySelector('label').click()")
            fc = fc_info.value
            fc.set_files(sample_file)
            print("  File chooser set for Sample Track. Waiting for upload...")
        except Exception as e:
            print(f"  File chooser error for sample: {e}")
            page.set_input_files('input[data-segment-id="3"]', sample_file)

        # Wait for sample flag
        for i in range(20):
            val = page.evaluate("() => document.querySelector('#HasSampleTrackHidden') ? document.querySelector('#HasSampleTrackHidden').value : ''")
            print(f"  [{i}s] HasSampleTrackHidden = {val}")
            if val == "True":
                print("✅ Sample Track confirmed!")
                break
            time.sleep(1)

if __name__ == "__main__":
    test_file_chooser()
