import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_tab1():
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

        tab1_info = page.evaluate("""() => {
            const result = {};
            
            // Contributors list / table
            const contribList = Array.from(document.querySelectorAll('.contributor-item, table, ul, .list-group-item, #ContributorList, [id*="Contributor"]'));
            result.contributors_html = contribList.map(c => ({ id: c.id, text: c.innerText.trim() })).filter(x => x.text.length > 0);

            // Radio selections
            const radios = Array.from(document.querySelectorAll('input[type="radio"]'));
            result.radios = radios.map(r => ({
                id: r.id,
                name: r.name,
                checked: r.checked,
                label: r.labels && r.labels[0] ? r.labels[0].innerText.trim() : (r.nextElementSibling ? r.nextElementSibling.innerText.trim() : '')
            }));

            // Errors / Validation messages
            const errors = Array.from(document.querySelectorAll('.text-danger, .field-validation-error, .error, .invalid-feedback'));
            result.errors = errors.map(e => e.innerText.trim()).filter(e => e.length > 0);

            // Buttons
            const buttons = Array.from(document.querySelectorAll('button, input[type="submit"]'));
            result.buttons = buttons.map(b => ({
                id: b.id,
                type: b.type,
                text: b.innerText.trim() || b.value,
                visible: !!(b.offsetWidth || b.offsetHeight || b.getClientRects().length)
            }));

            return result;
        }""")

        print("\n=== RADIOS ===")
        for r in tab1_info['radios']:
            print(f" ID: '{r['id']}' | Name: '{r['name']}' | Checked: {r['checked']} | Label: '{r['label']}'")

        print("\n=== CONTRIBUTORS SECTION ===")
        for c in tab1_info['contributors_html']:
            print(f" ID: '{c['id']}' | Text: {c['text'][:200]}")

        print("\n=== ERRORS ===")
        for e in tab1_info['errors']:
            print(f" Error: {e}")

        print("\n=== BUTTONS ===")
        for b in tab1_info['buttons']:
            print(f" ID: '{b['id']}' | Text: '{b['text']}' | Visible: {b['visible']}")

if __name__ == "__main__":
    inspect_tab1()
