import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def upload_via_cdp():
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

        client = context.new_cdp_session(page)
        client.send("DOM.enable")
        res = client.send("DOM.getFlattenedDocument", {"depth": -1, "pierce": True})
        nodes = res.get("nodes", [])

        def upload_segment_cdp(seg_id, files_list, name):
            if not files_list:
                return
            target_node_id = None
            for node in nodes:
                if node.get("nodeName") == "INPUT":
                    attrs = node.get("attributes", [])
                    attr_dict = dict(zip(attrs[::2], attrs[1::2]))
                    if attr_dict.get("data-segment-id") == str(seg_id):
                        target_node_id = node.get("nodeId")
                        break

            if target_node_id:
                print(f"CDP setting files for {name} (segment {seg_id}): {len(files_list)} file(s)...")
                client.send("DOM.setFileInputFiles", {
                    "files": files_list if isinstance(files_list, list) else [files_list],
                    "nodeId": target_node_id
                })
                page.evaluate(f"""() => {{
                    const el = document.querySelector('input[data-segment-id="{seg_id}"]');
                    if (el) {{
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                }}""")
                time.sleep(2)
            else:
                print(f"Could not find CDP nodeId for segment {seg_id}")

        # 1. Opening (Segment 1)
        upload_segment_cdp("1", payload.get('opening_track'), "Opening Track")
        
        # 2. Closing (Segment 2)
        upload_segment_cdp("2", payload.get('closing_track'), "Closing Track")
        
        # 3. Sample (Segment 3)
        upload_segment_cdp("3", payload.get('sample_track'), "Sample Track")

        # 4. Chapters (Segment 0)
        chapter_files = [f for f in payload['audio_tracks'] if "intro" not in f and "copyright" not in f]
        upload_segment_cdp("0", chapter_files, "Chapter Tracks")

        # Poll status flags for 30 seconds
        print("\n⏳ Polling hidden upload status flags...")
        for i in range(30):
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
                    chapters: chapters ? chapters.value : ''
                };
            }""")

            print(f"  [{i}s] Cover={status['cover']} | Opening={status['opening']} | Closing={status['closing']} | Sample={status['sample']} | Chapters={status['chapters']}")

            if (status['cover'] == "True" and 
                status['opening'] == "True" and 
                status['closing'] == "True" and 
                status['sample'] == "True" and 
                int(status['chapters'] or 0) >= len(chapter_files)):
                print("🎉 ALL UPLOAD FLAGS CONFIRMED TRUE!")
                break

            time.sleep(1)

if __name__ == "__main__":
    upload_via_cdp()
