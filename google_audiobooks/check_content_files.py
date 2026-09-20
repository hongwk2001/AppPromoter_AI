import os
import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_files(port=9222):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        files_on_page = page.evaluate("""
        () => {
            const rows = Array.from(document.querySelectorAll('tr, .file-row, .mat-row, mat-list-item, div'));
            const names = [];
            rows.forEach(r => {
                const txt = r.innerText || '';
                if (txt.includes('.mp3') || txt.includes('.jpg') || txt.includes('.png')) {
                    const match = txt.match(/([a-zA-Z0-9_\\-]+\\.(mp3|jpg|png))/g);
                    if (match) {
                        match.forEach(m => names.push(m));
                    }
                }
            });
            return Array.from(new Set(names));
        }
        """)

        print(f"Total uploaded files found on page: {len(files_on_page)}")
        print(json.dumps(files_on_page, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    check_files()
