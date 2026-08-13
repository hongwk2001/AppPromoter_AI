"""
inspect_d2d_form.py
Connects to an open Chrome instance on http://localhost:9222,
inspects all form fields on the active Draft2Digital page,
and saves the captured field selectors to a JSON file.
"""

import os
import sys
import json
import argparse
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")
os.makedirs(NOTES_DIR, exist_ok=True)

def inspect_active_page(port=9222, step_name="step1"):
    cdp_url = f"http://127.0.0.1:{port}"
    print(f"Connecting to Chrome via CDP at {cdp_url}...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}.")
            print(f"Details: {e}")
            print("\nPlease launch Chrome using:")
            print(r'  "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222')
            return

        context = browser.contexts[0]
        d2d_page = None
        
        # Search for tab containing draft2digital.com or active tab
        for page in context.pages:
            if "draft2digital.com" in page.url:
                d2d_page = page
                break
                
        if not d2d_page:
            # Fallback to the first active page
            if context.pages:
                d2d_page = context.pages[0]
                print(f"Notice: Draft2Digital domain not found in tabs. Inspecting current tab: {d2d_page.url}")
            else:
                print("Error: No open browser tabs found.")
                return

        print(f"Inspecting active page: {d2d_page.url} ({d2d_page.title()})\n")
        
        # JS script to scan and extract all form elements
        extraction_js = """
        () => {
            const elements = Array.from(document.querySelectorAll('input, textarea, select, button, label, [role="button"], [type="file"]'));
            const fieldList = [];
            
            elements.forEach((el, index) => {
                const tag = el.tagName.toLowerCase();
                const type = el.getAttribute('type') || '';
                const id = el.id || '';
                const name = el.getAttribute('name') || '';
                const placeholder = el.getAttribute('placeholder') || '';
                const ariaLabel = el.getAttribute('aria-label') || '';
                const role = el.getAttribute('role') || '';
                const isVisible = !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
                const value = el.value || '';
                
                // Associated label text
                let labelText = '';
                if (id) {
                    const labelEl = document.querySelector(`label[for="${id}"]`);
                    if (labelEl) labelText = labelEl.innerText.trim();
                }
                if (!labelText && el.closest('label')) {
                    labelText = el.closest('label').innerText.trim();
                }
                if (!labelText && el.previousElementSibling && el.previousElementSibling.tagName.toLowerCase() === 'label') {
                    labelText = el.previousElementSibling.innerText.trim();
                }

                // Best selector path
                let bestSelector = '';
                if (id) {
                    bestSelector = `#${id}`;
                } else if (name) {
                    bestSelector = `${tag}[name="${name}"]`;
                } else if (placeholder) {
                    bestSelector = `${tag}[placeholder="${placeholder}"]`;
                } else if (type === 'file') {
                    bestSelector = 'input[type="file"]';
                }

                fieldList.push({
                    index: index + 1,
                    tag: tag,
                    type: type,
                    id: id,
                    name: name,
                    placeholder: placeholder,
                    aria_label: ariaLabel,
                    role: role,
                    label_text: labelText,
                    value: value,
                    is_visible: isVisible,
                    best_selector: bestSelector
                });
            });
            
            return {
                url: window.location.href,
                title: document.title,
                timestamp: new Date().toISOString(),
                fields: fieldList
            };
        }
        """
        
        schema_data = d2d_page.evaluate(extraction_js)
        
        output_filename = f"d2d_form_schema_{step_name}.json"
        output_path = os.path.join(NOTES_DIR, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(schema_data, f, indent=2, ensure_ascii=False)
            
        print(f"Captured {len(schema_data['fields'])} form elements.")
        print(f"Saved form schema to: {output_path}\n")
        
        # Display summary table of key input/textarea/file fields
        print("=== Key Form Fields Summary ===")
        print(f"{'Idx':<4} | {'Tag/Type':<12} | {'Selector':<30} | {'Label/Placeholder'}")
        print("-" * 75)
        for field in schema_data['fields']:
            if field['tag'] in ['input', 'textarea', 'select'] or field['type'] == 'file':
                tag_type = f"{field['tag']}:{field['type']}" if field['type'] else field['tag']
                selector = field['best_selector'] or '(no id/name)'
                label = field['label_text'] or field['placeholder'] or field['aria_label'] or '-'
                print(f"{field['index']:<4} | {tag_type:<12} | {selector:<30} | {label[:30]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect Draft2Digital Form Fields via Playwright CDP")
    parser.add_argument("--port", type=int, default=9222, help="Chrome CDP debugging port (default: 9222)")
    parser.add_argument("--step", type=str, default="step1", help="Step name for output filename (e.g. step1, step2)")
    args = parser.parse_args()
    
    inspect_active_page(port=args.port, step_name=args.step)
