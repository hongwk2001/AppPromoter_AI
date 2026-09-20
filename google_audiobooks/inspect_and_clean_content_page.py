import os
import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_content_rows(port=9222):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        print(f"Connected to page: {page.url} ({page.title()})\n")

        row_info = page.evaluate("""
        () => {
            const rows = Array.from(document.querySelectorAll('tr, mat-row, div[role="row"], .file-row'));
            return rows.map((r, idx) => {
                const text = r.innerText ? r.innerText.replace(/\\n/g, ' | ') : '';
                const match = text.match(/([a-zA-Z0-9_\\-]+\\.(mp3|jpg|png))/i);
                const buttons = Array.from(r.querySelectorAll('button, mat-icon, a')).map(b => b.innerText || b.getAttribute('aria-label') || '');
                return {
                    idx: idx,
                    filename: match ? match[1] : '',
                    buttons: buttons.filter(b => b),
                    rowText: text.substring(0, 150)
                };
            }).filter(r => r.filename || r.rowText.includes('.mp3'));
        }
        """)

        print(f"Total file rows found: {len(row_info)}")
        print(json.dumps(row_info, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    inspect_content_rows()
