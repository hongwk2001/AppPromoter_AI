import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def wait_for_ar_uploads_complete(page, expected_chapters=13, timeout_sec=180):
    print("⏳ Waiting for all track uploads and hidden status flags to confirm...")
    start_time = time.time()
    while time.time() - start_time < timeout_sec:
        status = page.evaluate("""() => {
            const cover = document.querySelector('#HasCoverImageHidden');
            const opening = document.querySelector('#HasOpeningTrackHidden');
            const closing = document.querySelector('#HasClosingTrackHidden');
            const sample = document.querySelector('#HasSampleTrackHidden');
            const chapters = document.querySelector('#HasChapterTrackHidden');

            return {
                cover: cover ? cover.value : '',
                opening: opening ? opening.value : '',
                closing: closing ? closing.value : '',
                sample: sample ? sample.value : '',
                chapters: chapters ? chapters.value : '',
                progressModal: !!document.querySelector('#UploadProgressModal.show'),
                toasts: Array.from(document.querySelectorAll('.toast-body')).map(t => t.innerText.trim())
            };
        }""")

        print(f"  Upload Status [{int(time.time() - start_time)}s]: Cover={status['cover']}, Opening={status['opening']}, Closing={status['closing']}, Sample={status['sample']}, Chapters={status['chapters']}")

        all_ready = (
            status['cover'] == "True" and
            status['opening'] == "True" and
            status['closing'] == "True" and
            status['sample'] == "True" and
            int(status['chapters'] or 0) >= expected_chapters and
            not status['progressModal']
        )

        if all_ready:
            print("✅ All track uploads verified successfully!")
            return True

        time.sleep(3)

    print("⚠️ Warning: Timed out waiting for all upload flags to confirm.")
    return False

def upload_all_and_verify():
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

        print(f"Uploading files for: {payload['title']}")
        
        # Cover image
        if payload.get('cover_path') and os.path.exists(payload['cover_path']):
            print(f"Uploading Cover: {payload['cover_path']}")
            page.set_input_files("#square-cover-file", payload['cover_path'])
            time.sleep(2)

        inputs = page.query_selector_all("input.chunkUploader")
        print(f"Found {len(inputs)} audio upload inputs.")

        # Opening
        if len(inputs) >= 1 and payload.get('opening_track') and os.path.exists(payload['opening_track']):
            print(f"Uploading Opening: {payload['opening_track']}")
            inputs[0].set_input_files(payload['opening_track'])
            time.sleep(3)

        # Closing
        if len(inputs) >= 2 and payload.get('closing_track') and os.path.exists(payload['closing_track']):
            print(f"Uploading Closing: {payload['closing_track']}")
            inputs[1].set_input_files(payload['closing_track'])
            time.sleep(3)

        # Sample
        if len(inputs) >= 3 and payload.get('sample_track') and os.path.exists(payload['sample_track']):
            print(f"Uploading Sample: {payload['sample_track']}")
            inputs[2].set_input_files(payload['sample_track'])
            time.sleep(3)

        # Chapters
        chapter_files = [f for f in payload['audio_tracks'] if "intro" not in f and "copyright" in f or ("final_ch_" in f)]
        print(f"Uploading {len(chapter_files)} Chapter Tracks...")
        
        # Native CDP DOM manipulation for bulk chapter selection
        try:
            client = context.new_cdp_session(page)
            doc = client.send("DOM.getDocument")
            root_id = doc["root"]["nodeId"]
            res = client.send("DOM.querySelectorAll", {
                "nodeId": root_id,
                "selector": 'input[data-segment-id="0"]'
            })
            if res.get("nodeIds"):
                target_node_id = res["nodeIds"][0]
                client.send("DOM.setFileInputFiles", {
                    "files": chapter_files,
                    "nodeId": target_node_id
                })
                time.sleep(1)
                page.evaluate("""() => {
                    const el = document.querySelector('input[data-segment-id="0"]');
                    if (el) {
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }""")
        except Exception as e:
            print(f"CDP error: {e}")

        # Wait for all upload flags to confirm
        num_chapters = len(chapter_files)
        wait_for_ar_uploads_complete(page, expected_chapters=num_chapters, timeout_sec=180)

        # Click AgreementBtn to move to Tab 4
        print("Navigating to Tab 4...")
        if page.is_visible("#AgreementBtn"):
            try:
                page.click("#AgreementBtn", timeout=10000)
            except Exception:
                page.evaluate("() => { const b = document.querySelector('#AgreementBtn'); if(b) b.click(); }")
            time.sleep(3)

        # Tab 4 checkboxes
        print("Checking Tab 4 checkboxes...")
        checkboxes = page.query_selector_all("input[type='checkbox']")
        for cb in checkboxes:
            if not cb.is_checked():
                cb.check()
                time.sleep(0.3)

        print("🎉 Complete 4-Tab workflow finished!")

if __name__ == "__main__":
    upload_all_and_verify()
