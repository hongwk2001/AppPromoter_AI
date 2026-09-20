import os
import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_modal(port=9222):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        modal_info = page.evaluate("""
        () => {
            const dialog = document.querySelector('mat-dialog-container, div[role="dialog"]');
            if (!dialog) return { hasDialog: false };

            const buttons = Array.from(dialog.querySelectorAll('button, [role="button"], a')).map(b => ({
                text: b.innerText.trim(),
                class: b.className,
                visible: b.offsetWidth > 0 && b.offsetHeight > 0
            }));

            const inputs = Array.from(dialog.querySelectorAll('input')).map(i => ({
                type: i.type,
                id: i.id,
                name: i.name,
                class: i.className,
                accept: i.accept || ''
            }));

            return {
                hasDialog: true,
                dialogText: dialog.innerText.substring(0, 300).replace(/\\n/g, ' '),
                buttons: buttons,
                inputs: inputs
            };
        }
        """)

        print(json.dumps(modal_info, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    inspect_modal()
