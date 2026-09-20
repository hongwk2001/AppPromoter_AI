import sys
import json
import urllib.request
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_page():
    cdp_url = "http://127.0.0.1:9222"
    print(f"Connecting to Chrome on {cdp_url}...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            print(f"Failed to connect to Chrome on port 9222: {e}")
            print("Make sure Chrome is running with --remote-debugging-port=9222")
            return
        
        context = browser.contexts[0]
        print(f"Found {len(context.pages)} open pages.")
        
        target_page = None
        for page in context.pages:
            print(f"  Page URL: {page.url} | Title: {page.title()}")
            if "authorsrepublic.com" in page.url:
                target_page = page
        
        if not target_page:
            print("Authors Republic tab not found. Using current active page:")
            if context.pages:
                target_page = context.pages[0]
            else:
                print("No pages open.")
                return

        print(f"\nTargeting page: {target_page.url}")
        
        # Extract tab buttons / elements
        tabs_info = target_page.evaluate("""() => {
            const result = {};
            
            // Look for nav tabs, headers, steps
            const tabs = Array.from(document.querySelectorAll('ul.nav-tabs li, nav a, .steps .step, div[role="tab"], button[role="tab"], .tab, .wizard-steps li, a.nav-link, .nav-item'));
            result.tabs = tabs.map(t => ({
                text: t.innerText.trim().replace(/\\n+/g, ' '),
                class: t.className,
                id: t.id,
                active: t.classList.contains('active') || t.getAttribute('aria-selected') === 'true'
            }));

            // Look for inputs, textareas, selects, file inputs
            const inputs = Array.from(document.querySelectorAll('input, select, textarea, button'));
            result.form_controls = inputs.map(el => ({
                tag: el.tagName.toLowerCase(),
                type: el.type || '',
                name: el.name || '',
                id: el.id || '',
                placeholder: el.placeholder || '',
                value: el.value ? el.value.substring(0, 50) : '',
                label: el.labels && el.labels[0] ? el.labels[0].innerText.trim() : (el.closest('label') ? el.closest('label').innerText.trim() : ''),
                text: (el.tagName === 'BUTTON' || el.type === 'submit') ? el.innerText.trim() : ''
            })).filter(item => item.id || item.name || item.text || item.label);

            result.url = window.location.href;
            result.title = document.title;

            return result;
        }""")
        
        print("\n--- DOM Inspection Results ---")
        print(f"Page Title: {tabs_info.get('title')}")
        print(f"Page URL:   {tabs_info.get('url')}")
        print(f"\nTabs found ({len(tabs_info.get('tabs', []))}):")
        for idx, t in enumerate(tabs_info.get('tabs', []), 1):
            print(f"  [{idx}] {t['text']} (Active: {t['active']}, Class: {t['class']})")

        print(f"\nForm Controls sample ({len(tabs_info.get('form_controls', []))} total):")
        for fc in tabs_info.get('form_controls', [])[:40]:
            print(f"  <{fc['tag']}> type='{fc['type']}' id='{fc['id']}' name='{fc['name']}' label='{fc['label']}' text='{fc['text']}'")

        # Save full dump to json file
        dump_path = "authors_republic_dom_dump.json"
        with open(dump_path, "w", encoding="utf-8") as f:
            json.dump(tabs_info, f, ensure_ascii=False, indent=2)
        print(f"\nFull inspection output saved to {dump_path}")

if __name__ == "__main__":
    inspect_page()
