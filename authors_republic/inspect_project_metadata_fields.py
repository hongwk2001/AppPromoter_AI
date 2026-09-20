import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_project_form():
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

        # Navigate to edit page for 73477
        print("Navigating to https://www.authorsrepublic.com/the-republic/projects/publish-a-book?projectId=73477...")
        page.goto("https://www.authorsrepublic.com/the-republic/projects/publish-a-book?projectId=73477")
        page.wait_for_load_state("networkidle")

        radios_and_inputs = page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('input, select, label'));
            return els.map(el => {
                let label = '';
                if (el.labels && el.labels[0]) label = el.labels[0].innerText.trim();
                else if (el.closest('label')) label = el.closest('label').innerText.trim();
                else if (el.previousElementSibling && el.previousElementSibling.tagName === 'LABEL') label = el.previousElementSibling.innerText.trim();

                return {
                    tag: el.tagName.toLowerCase(),
                    type: el.type || '',
                    id: el.id || '',
                    name: el.name || '',
                    label: label,
                    value: el.value || '',
                    checked: el.checked || false,
                    visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)
                };
            }).filter(x => x.visible || x.type === 'radio' || x.type === 'checkbox');
        }""")

        print(f"Form controls found on projectId=73477 ({len(radios_and_inputs)}):")
        for item in radios_and_inputs:
            if item['type'] in ['radio', 'checkbox'] or 'domain' in item['name'].lower() or 'domain' in item['id'].lower():
                print(f" <{item['tag'].upper()}> type='{item['type']}' id='{item['id']}' name='{item['name']}' checked={item['checked']} label='{item['label']}'")

if __name__ == "__main__":
    check_project_form()
