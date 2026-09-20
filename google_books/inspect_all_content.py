import os
import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_open_page(port=9222):
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error connecting to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        if not pages:
            print("No Google Books page found in open Chrome tabs.")
            return

        page = pages[0]
        print(f"==================================================")
        print(f"📖 Active Page URL:   {page.url}")
        print(f"📖 Active Page Title: {page.title()}")
        print(f"==================================================\n")

        report = page.evaluate("""
        () => {
            const subTabs = Array.from(document.querySelectorAll('a[mat-tab-link], div[role="tab"]')).map(t => ({
                text: t.innerText.trim().replace(/\\n/g, ' '),
                active: t.classList.contains('mdc-tab--active') || t.getAttribute('aria-selected') === 'true'
            }));

            const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]), textarea, mat-select')).map(i => {
                const ff = i.closest('mat-form-field');
                const label = ff ? (ff.querySelector('label, mat-label') ? ff.querySelector('label, mat-label').innerText.trim() : ff.innerText.split('\\n')[0]) : '';
                return {
                    label: label,
                    placeholder: i.placeholder || '',
                    value: (i.value || i.innerText || '').trim().replace(/\\n/g, ' '),
                    tag: i.tagName,
                    visible: i.offsetWidth > 0 && i.offsetHeight > 0
                };
            }).filter(i => i.visible && (i.label || i.placeholder || i.value));

            const filesOnPage = Array.from(document.querySelectorAll('tr, .file-row, mat-row')).map(r => {
                const txt = r.innerText || '';
                const match = txt.match(/([a-zA-Z0-9_\\-]+\\.(mp3|jpg|png))/g);
                return match ? match[0] : null;
            }).filter(Boolean);

            return {
                subTabs: subTabs,
                inputs: inputs,
                uniqueFilesOnPageCount: Array.from(new Set(filesOnPage)).length,
                filenamesSample: Array.from(new Set(filesOnPage)).slice(0, 10)
            };
        }
        """)

        print("📋 SUB-TABS STATUS:")
        for st in report.get("subTabs", []):
            active_str = " (ACTIVE)" if st["active"] else ""
            print(f"  • {st['text']}{active_str}")

        print("\n📋 VISIBLE INPUT FIELDS & VALUES:")
        for inp in report.get("inputs", []):
            lbl = inp["label"] or inp["placeholder"] or inp["tag"]
            val_preview = inp["value"][:60] + "..." if len(inp["value"]) > 60 else inp["value"]
            print(f"  • {lbl}: {val_preview}")

        print(f"\n📋 CONTENT FILES ON PAGE:")
        print(f"  • Total Unique File Rows Detected: {report.get('uniqueFilesOnPageCount', 0)}")
        if report.get("filenamesSample"):
            print(f"  • Sample Files: {', '.join(report['filenamesSample'])}")

if __name__ == "__main__":
    check_open_page()
