import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_live():
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

        upload_state = page.evaluate("""() => {
            const files = Array.from(document.querySelectorAll('.file-item, .track-item, .uploaded-file, .dz-preview, .audio-file-row, table tr')).map(f => f.innerText.replace(/\\n+/g, ' ').trim()).filter(x => x.length > 0);
            const coverImg = document.querySelector('#square-cover-wrapper img, .cover-image img');
            const progressModal = document.querySelector('#UploadProgressModal');
            return {
                uploaded_items: files.slice(0, 20),
                cover_image_src: coverImg ? coverImg.src : 'None',
                progress_visible: progressModal ? !!(progressModal.offsetWidth || progressModal.offsetHeight) : false
            };
        }""")

        print(f"Cover Image Uploaded: {upload_state['cover_image_src']}")
        print(f"Progress Modal Visible: {upload_state['progress_visible']}")
        print(f"Uploaded Files / Tracks list ({len(upload_state['uploaded_items'])}):")
        for item in upload_state['uploaded_items'][:15]:
            print(f"  - {item}")

if __name__ == "__main__":
    check_live()
