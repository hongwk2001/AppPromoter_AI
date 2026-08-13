"""
select_all_channels_js.py
Instantly checks ALL supported digital stores, library services, and subscription channels on Draft2Digital Step 3.
"""

import os
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def select_all():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "draft2digital.com" in pg.url][0]
        
        js = """
        () => {
            const targets = Array.from(document.querySelectorAll('div.toggle[aria-disabled="false"][aria-checked="false"], div[role="checkbox"][aria-disabled="false"][aria-checked="false"]'));
            const selected = [];
            targets.forEach(cb => {
                const tr = cb.closest('tr');
                const title = tr ? (tr.getAttribute('title') || tr.innerText.split('\\n')[0]) : 'Channel';
                cb.click();
                selected.push(title);
            });
            return selected;
        }
        """
        results = page.evaluate(js)
        print(f"✅ Successfully checked {len(results)} supported distribution channels!")
        for name in results:
            print(f"  ✓ Checked: {name}")

if __name__ == "__main__":
    select_all()
