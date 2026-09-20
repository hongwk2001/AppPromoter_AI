import json
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_dom(port=9222):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        pages = [pg for pg in browser.contexts[0].pages if "content" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page: {page.url} ({page.title()})")

        dom_info = page.evaluate("""
        () => {
            const fileInputs = Array.from(document.querySelectorAll('input[type="file"]')).map(i => ({
                id: i.id,
                name: i.name,
                accept: i.accept,
                multiple: i.multiple,
                outer: i.outerHTML
            }));

            const buttons = Array.from(document.querySelectorAll('button, [role="button"], a.mat-button, a.mat-raised-button, a.mat-flat-button')).map(b => ({
                text: (b.innerText || b.getAttribute('aria-label') || '').trim(),
                tag: b.tagName,
                class: b.className,
                outer: b.outerHTML.slice(0, 200)
            }));

            const dropZones = Array.from(document.querySelectorAll('[class*="drop"], [class*="upload"], [id*="upload"], [id*="drop"]')).map(d => ({
                text: (d.innerText || '').slice(0, 100),
                outer: d.outerHTML.slice(0, 200)
            }));

            return {
                fileInputs,
                buttons: buttons.filter(b => b.text.length > 0 && b.text.length < 80),
                dropZones
            };
        }
        """)

        print("\n--- FILE INPUTS ---")
        print(json.dumps(dom_info["fileInputs"], indent=2, ensure_ascii=False))

        print("\n--- BUTTONS ---")
        print(json.dumps(dom_info["buttons"], indent=2, ensure_ascii=False))

        print("\n--- DROP ZONES ---")
        print(json.dumps(dom_info["dropZones"], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    inspect_dom()
