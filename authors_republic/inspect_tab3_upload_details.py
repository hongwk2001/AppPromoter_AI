import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_tab3_details():
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

        upload_info = page.evaluate("""() => {
            const result = {};
            
            // All file inputs (hidden or visible)
            const fileInputs = Array.from(document.querySelectorAll('input[type="file"]'));
            result.file_inputs = fileInputs.map(f => ({
                id: f.id,
                name: f.name,
                class: f.className,
                accept: f.accept,
                multiple: f.multiple,
                parent_id: f.parentElement ? f.parentElement.id : '',
                parent_class: f.parentElement ? f.parentElement.className : ''
            }));

            // All forms and dropzones
            const dropzones = Array.from(document.querySelectorAll('form, div, section')).filter(el => {
                const id = el.id.toLowerCase();
                const cls = el.className.toLowerCase();
                return id.includes('cover') || id.includes('audio') || id.includes('upload') || id.includes('drop') || id.includes('file') ||
                       cls.includes('cover') || cls.includes('audio') || cls.includes('upload') || cls.includes('drop') || cls.includes('file');
            });

            result.dropzones = dropzones.map(d => ({
                tag: d.tagName.toLowerCase(),
                id: d.id,
                class: d.className,
                text: d.innerText ? d.innerText.substring(0, 150).replace(/\\n+/g, ' ') : ''
            }));

            // Buttons
            const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], a.btn'));
            result.buttons = buttons.map(b => ({
                id: b.id,
                class: b.className,
                text: b.innerText ? b.innerText.trim() : b.value,
                visible: !!(b.offsetWidth || b.offsetHeight || b.getClientRects().length)
            })).filter(x => x.visible);

            return result;
        }""")

        print(f"\n=== FILE INPUTS ({len(upload_info['file_inputs'])}) ===")
        for f in upload_info['file_inputs']:
            print(f" <INPUT type='file'> id='{f['id']}' name='{f['name']}' class='{f['class']}' accept='{f['accept']}' multiple={f['multiple']} | Parent: {f['parent_id']} ({f['parent_class']})")

        print(f"\n=== UPLOAD CONTAINERS / DROPZONES ({len(upload_info['dropzones'])}) ===")
        for d in upload_info['dropzones']:
            print(f" <{d['tag'].upper()}> id='{d['id']}' class='{d['class']}' text='{d['text'][:80]}'")

        print(f"\n=== VISIBLE BUTTONS ({len(upload_info['buttons'])}) ===")
        for b in upload_info['buttons']:
            print(f" <{b['id']}> text='{b['text']}' class='{b['class']}'")

if __name__ == "__main__":
    inspect_tab3_details()
