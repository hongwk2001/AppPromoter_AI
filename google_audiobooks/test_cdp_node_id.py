import time
import os
import sys
import glob
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_node():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = [pg for pg in browser.contexts[0].pages if "content" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        audio_dir = r"C:\git_repo\TKprof_book\books\blue_castle\final_audio_ko"
        mp3_files = glob.glob(os.path.join(audio_dir, "*.mp3"))

        def sort_key(p):
            fname = os.path.basename(p)
            if "intro" in fname:
                return (0, 0)
            elif "closing" in fname:
                return (2, 9999)
            else:
                nums = "".join([ch for ch in fname if ch.isdigit()])
                return (1, int(nums) if nums else 500)

        mp3_files.sort(key=sort_key)

        # Click browse button inside dialog
        browse_btn = page.locator('mat-dialog-container button[xapuploadertrigger], mat-dialog-container button:has-text("Browse")').first
        if browse_btn.count() > 0:
            browse_btn.click(force=True)
            time.sleep(1)

        client = page.context.new_cdp_session(page)
        client.send("DOM.enable")

        # Get element handle
        elem = page.locator('input[type="file"]').first
        elem.scroll_into_view_if_needed()

        # Get Document Node ID and search
        doc = client.send("DOM.getDocument", {"depth": -1, "pierce": True})
        nodes = client.send("DOM.performSearch", {"query": '//input[@type="file"]'})
        search_id = nodes["searchId"]
        result = client.send("DOM.getSearchResult", {
            "searchId": search_id,
            "fromIndex": 0,
            "toIndex": nodes["resultCount"]
        })

        if result["nodeIds"]:
            target_node_id = result["nodeIds"][-1]
            print(f"Found Node ID via search: {target_node_id}")

            client.send("DOM.setFileInputFiles", {
                "files": mp3_files,
                "nodeId": target_node_id
            })
            print(f"✅ ONE-SHOT SUCCESS: Set all {len(mp3_files)} MP3 audio files via CDP DOM.setFileInputFiles!")

            page.evaluate("""
            () => {
                const inp = document.querySelector('input[type="file"]');
                if (inp) {
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
            """)

if __name__ == "__main__":
    test_node()
