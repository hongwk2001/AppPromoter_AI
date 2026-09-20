import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_tab3():
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

        tab3_info = page.evaluate("""() => {
            const result = {};
            const active = document.querySelector('.w-20.active, .nav-tabs .active, .wizard-steps .active, [aria-selected="true"]');
            result.active_tab = active ? active.innerText.trim() : 'Unknown';

            // Check for file inputs / dropzones / audio upload containers
            const fileInputs = Array.from(document.querySelectorAll('input[type="file"]'));
            result.file_inputs = fileInputs.map(f => ({
                id: f.id,
                name: f.name,
                accept: f.accept,
                multiple: f.multiple,
                visible: !!(f.offsetWidth || f.offsetHeight || f.getClientRects().length)
            }));

            const dropzones = Array.from(document.querySelectorAll('.dropzone, [id*="drop"], [class*="drop"], [id*="upload"], [class*="upload"]'));
            result.dropzones = dropzones.map(d => ({
                tag: d.tagName.toLowerCase(),
                id: d.id,
                class: d.className,
                text: d.innerText ? d.innerText.substring(0, 100).replace(/\\n+/g, ' ') : ''
            }));

            const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], a.btn'));
            result.buttons = buttons.map(b => ({
                id: b.id,
                text: b.innerText ? b.innerText.trim() : b.value,
                visible: !!(b.offsetWidth || b.offsetHeight || b.getClientRects().length)
            })).filter(x => x.visible);

            return result;
        }""")

        print(f"Active Tab: {tab3_info['active_tab']}")
        print(f"\nFile Inputs found ({len(tab3_info['file_inputs'])}):")
        for f in tab3_info['file_inputs']:
            print(f"  <INPUT type='file'> id='{f['id']}' name='{f['name']}' accept='{f['accept']}' multiple={f['multiple']}")

        print(f"\nDropzones / Upload Areas ({len(tab3_info['dropzones'])}):")
        for d in tab3_info['dropzones']:
            print(f"  <{d['tag']}> id='{d['id']}' class='{d['class']}' text='{d['text'][:60]}'")

        print(f"\nVisible Buttons ({len(tab3_info['buttons'])}):")
        for b in tab3_info['buttons']:
            print(f"  <{b['id']}> text='{b['text']}'")

if __name__ == "__main__":
    inspect_tab3()
