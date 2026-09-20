import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def interactive_upload():
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

        print("\n🚀 Uploading all audio tracks via Playwright FileChooser...")

        def upload_via_chooser(segment_id, file_paths, label_name):
            files = file_paths if isinstance(file_paths, list) else [file_paths]
            valid_files = [f for f in files if f and os.path.exists(f)]
            if not valid_files:
                print(f"⚠️ No valid files found for {label_name}")
                return

            print(f"\nUploading {label_name} ({len(valid_files)} file(s))...")
            try:
                # Find selector for segment_id label
                input_sel = f'input[data-segment-id="{segment_id}"]'
                page.wait_for_selector(input_sel, state="attached", timeout=5000)

                with page.expect_file_chooser(timeout=10000) as fc_info:
                    # Click parent label or input
                    page.eval_on_selector(input_sel, "el => (el.parentElement || el).click()")
                
                fc = fc_info.value
                fc.set_files(valid_files)
                print(f"  ✅ FileChooser set {len(valid_files)} file(s) for {label_name}")
                time.sleep(3.0)

            except Exception as e:
                print(f"  ❌ Error uploading {label_name}: {e}")
                # Fallback to direct set_input_files
                try:
                    page.set_input_files(input_sel, valid_files)
                    print(f"  ✅ Fallback direct set_input_files succeeded for {label_name}")
                    time.sleep(3.0)
                except Exception as e2:
                    print(f"  ❌ Fallback error for {label_name}: {e2}")

        # 1. Opening Track (Segment ID 1)
        upload_via_chooser("1", payload.get('opening_track'), "Opening Track")

        # 2. Closing Track (Segment ID 2)
        upload_via_chooser("2", payload.get('closing_track'), "Closing Track")

        # 3. Sample Track (Segment ID 3)
        upload_via_chooser("3", payload.get('sample_track'), "Sample Track")

        # 4. Chapter Tracks (Segment ID 0)
        chapter_files = [
            f for f in payload['audio_tracks']
            if not any(k in os.path.basename(f).lower() for k in ["opening", "ending", "intro", "closing", "sample", "podcast"])
        ]
        upload_via_chooser("0", chapter_files, "Chapter Tracks")

        # Monitor upload progress modal / hidden flags
        print("\n⏳ Polling upload completion status flags for 60s...")
        for i in range(20):
            status = page.evaluate("""() => {
                return {
                    opening: document.querySelector('#HasOpeningTrackHidden') ? document.querySelector('#HasOpeningTrackHidden').value : '',
                    closing: document.querySelector('#HasClosingTrackHidden') ? document.querySelector('#HasClosingTrackHidden').value : '',
                    sample: document.querySelector('#HasSampleTrackHidden') ? document.querySelector('#HasSampleTrackHidden').value : '',
                    chapters: document.querySelector('#HasChapterTrackHidden') ? document.querySelector('#HasChapterTrackHidden').value : '',
                    modal: !!document.querySelector('#UploadProgressModal.show')
                };
            }""")
            print(f"  [{i*3}s] Opening={status['opening']} | Closing={status['closing']} | Sample={status['sample']} | Chapters={status['chapters']} | UploadingModal={status['modal']}")
            if (status['opening'] == "True" and 
                status['closing'] == "True" and 
                status['sample'] == "True" and 
                int(status['chapters'] or 0) >= len(chapter_files) and 
                not status['modal']):
                print("🎉 ALL TRACKS FULLY UPLOADED AND CONFIRMED!")
                break
            time.sleep(3.0)

if __name__ == "__main__":
    interactive_upload()
