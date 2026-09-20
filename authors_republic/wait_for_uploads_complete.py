import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def wait_for_uploads():
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

        print("Waiting for file upload processing modal (#UploadProgressModal) to complete...")
        for i in range(30):
            is_modal_visible = page.evaluate("""() => {
                const m = document.querySelector('#UploadProgressModal');
                return m ? !!(m.offsetWidth || m.offsetHeight || m.getClientRects().length) : false;
            }""")
            if not is_modal_visible:
                print("✅ Upload progress modal is closed!")
                break
            print(f"  Uploading in progress... ({i*2}s)")
            time.sleep(2.0)

        # Check track items after upload
        tracks_info = page.evaluate("""() => {
            const rows = Array.from(document.querySelectorAll('.audio-file-item, .audio-track-row, .track-name, div[id*="track"], tr')).map(r => r.innerText.replace(/\\n+/g, ' ').trim()).filter(t => t.length > 0 && t.includes('.mp3'));
            return rows;
        }""")

        print(f"\nUploaded tracks detected ({len(tracks_info)}):")
        for t in tracks_info[:20]:
            print(f"  🎵 {t[:80]}")

if __name__ == "__main__":
    wait_for_uploads()
