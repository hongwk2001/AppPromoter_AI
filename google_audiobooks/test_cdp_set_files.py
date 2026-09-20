import time
import os
import sys
import glob
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_cdp_files():
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
        print(f"Targeting input[type='file'] via CDP with {len(mp3_files)} MP3 files...")

        # Create CDP session directly with the target page
        client = page.context.new_cdp_session(page)

        # Get node ID of input[type="file"]
        doc = client.send("DOM.getDocument")
        node = client.send("DOM.querySelector", {
            "nodeId": doc["root"]["nodeId"],
            "selector": 'input[type="file"]'
        })
        node_id = node["nodeId"]
        print(f"Found DOM Node ID: {node_id}")

        # Set files directly via CDP protocol without base64 transfer!
        client.send("DOM.setFileInputFiles", {
            "files": mp3_files,
            "nodeId": node_id
        })
        print(f"✅ Successfully set {len(mp3_files)} files via CDP DOM.setFileInputFiles in ONE SHOT!")

        # Dispatch change & input events on the input element
        page.evaluate("""
        () => {
            const inp = document.querySelector('input[type="file"]');
            if (inp) {
                inp.dispatchEvent(new Event('input', { bubbles: true }));
                inp.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
        """)
        print("✓ Dispatched change event on input element!")

if __name__ == "__main__":
    test_cdp_files()
