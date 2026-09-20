import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_sample_input():
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

        print(f"URL: {page.url}")

        sample_info = page.evaluate("""() => {
            const containers = Array.from(document.querySelectorAll('.upload-file-col, .audio-file-wrapper, div[class*="upload"]'));
            const results = [];

            for (const c of containers) {
                const text = c.innerText.replace(/\\n+/g, ' ').trim();
                if (text.includes('Sample Track') || text.includes('Opening Track') || text.includes('Closing Track') || text.includes('Chapter Tracks')) {
                    const input = c.querySelector('input[type="file"]');
                    results.push({
                        text: text.substring(0, 100),
                        has_input: !!input,
                        input_id: input ? input.id : '',
                        input_class: input ? input.className : '',
                        input_name: input ? input.name : '',
                        input_accept: input ? input.accept : '',
                        input_multiple: input ? input.multiple : false
                    });
                }
            }

            // Get all input[type="file"] on entire page
            const allFileInputs = Array.from(document.querySelectorAll('input[type="file"]')).map((f, idx) => ({
                index: idx,
                id: f.id,
                name: f.name,
                class: f.className,
                accept: f.accept,
                multiple: f.multiple,
                parent_text: f.parentElement ? f.parentElement.innerText.substring(0, 80).replace(/\\n+/g, ' ') : ''
            }));

            return {
                containers: results,
                all_file_inputs: allFileInputs
            };
        }""")

        print("\n=== AUDIO TRACK UPLOAD CONTAINERS ===")
        for c in sample_info['containers']:
            print(f" Text: '{c['text']}' | Has Input: {c['has_input']} | Input ID: '{c['input_id']}' | Input Class: '{c['input_class']}'")

        print("\n=== ALL FILE INPUTS ON PAGE ===")
        for f in sample_info['all_file_inputs']:
            print(f" Index [{f['index']}]: id='{f['id']}' class='{f['class']}' multiple={f['multiple']} | Parent Text: '{f['parent_text']}'")

if __name__ == "__main__":
    inspect_sample_input()
