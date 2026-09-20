import os
import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_active(port=9222):
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        print(f"URL: {page.url}")
        print(f"Title: {page.title()}\n")

        info = page.evaluate("""
        () => {
            const activeTab = document.querySelector('a.mdc-tab--active, div.mat-mdc-tab-active, [aria-selected="true"]');
            const subTabs = Array.from(document.querySelectorAll('a[mat-tab-link], div[role="tab"]')).map(t => ({
                text: t.innerText.trim(),
                href: t.getAttribute('href') || '',
                active: t.classList.contains('mdc-tab--active') || t.getAttribute('aria-selected') === 'true'
            }));

            const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]), textarea, mat-select')).map(i => {
                const ff = i.closest('mat-form-field');
                return {
                    tag: i.tagName,
                    id: i.id || '',
                    placeholder: i.placeholder || '',
                    value: i.value || i.innerText || '',
                    formFieldText: ff ? ff.innerText.replace(/\\n/g, ' ').substring(0, 80) : '',
                    isVisible: i.offsetWidth > 0 && i.offsetHeight > 0
                };
            });

            return {
                activeTabName: activeTab ? activeTab.innerText.trim() : 'Unknown',
                subTabs: subTabs,
                inputs: inputs
            };
        }
        """)

        print(json.dumps(info, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    inspect_active()
