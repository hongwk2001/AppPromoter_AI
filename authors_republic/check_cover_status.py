import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_cover():
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

        cover_state = page.evaluate("""() => {
            const wrapper = document.querySelector('#square-cover-wrapper');
            const img = document.querySelector('#square-cover-wrapper img, .cover-image img, img[id*="cover"]');
            return {
                wrapper_html: wrapper ? wrapper.innerHTML.substring(0, 300) : 'Not found',
                img_src: img ? img.src : 'No <img> tag found',
                wrapper_text: wrapper ? wrapper.innerText.trim() : ''
            };
        }""")

        print(f"Cover Image Section: {cover_state['wrapper_text']}")
        print(f"Cover <img> src: {cover_state['img_src']}")

if __name__ == "__main__":
    check_cover()
