import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def test_closing():
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
        print(f"Uploading Closing Track: {closing_file}")
        
        # Method 1: Playwright set_input_files
        page.set_input_files('input[data-segment-id="2"]', closing_file)
        page.evaluate("""() => {
            const el = document.querySelector('input[data-segment-id="2"]');
            if (el) {
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""")

        # Poll status for 15 seconds
        for i in range(15):
            val = page.evaluate("() => document.querySelector('#HasClosingTrackHidden') ? document.querySelector('#HasClosingTrackHidden').value : ''")
            print(f"  [{i}s] HasClosingTrackHidden = {val}")
            if val == "True":
                print("✅ Closing track confirmed upload!")
                break
            time.sleep(1)

        # Method 2: If still False, attempt CDP setFileInputFiles
        val = page.evaluate("() => document.querySelector('#HasClosingTrackHidden') ? document.querySelector('#HasClosingTrackHidden').value : ''")
        if val != "True":
            print("Attempting CDP input files set for segment 2...")
            client = context.new_cdp_session(page)
            doc = client.send("DOM.getDocument")
            root_id = doc["root"]["nodeId"]
            res = client.send("DOM.querySelectorAll", {
                "nodeId": root_id,
                "selector": 'input[data-segment-id="2"]'
            })
            if res.get("nodeIds"):
                target_node_id = res["nodeIds"][0]
                client.send("DOM.setFileInputFiles", {
                    "files": [closing_file],
                    "nodeId": target_node_id
                })
                page.evaluate("""() => {
                    const el = document.querySelector('input[data-segment-id="2"]');
                    if (el) {
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }""")

            for i in range(15):
                val = page.evaluate("() => document.querySelector('#HasClosingTrackHidden') ? document.querySelector('#HasClosingTrackHidden').value : ''")
                print(f"  [CDP {i}s] HasClosingTrackHidden = {val}")
                if val == "True":
                    print("✅ Closing track confirmed via CDP!")
                    break
                time.sleep(1)

if __name__ == "__main__":
    test_closing()
