import sys
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_audio_fields():
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
            print("No page found")
            return

        fields = page.evaluate("""() => {
            const fileInputs = Array.from(document.querySelectorAll('input[type="file"]'));
            return fileInputs.map(input => {
                let parentLabel = input.closest('.form-group, .mb-3, div, label') ? input.closest('.form-group, .mb-3, div, label').innerText.trim().replace(/\\s+/g, ' ') : '';
                let prevLabel = input.previousElementSibling && input.previousElementSibling.tagName === 'LABEL' ? input.previousElementSibling.innerText.trim() : '';
                
                return {
                    id: input.id,
                    name: input.name,
                    class: input.className,
                    dataSegmentId: input.getAttribute('data-segment-id') || '',
                    dataAudioId: input.getAttribute('data-audio-id') || '',
                    dataKind: input.getAttribute('data-kind') || '',
                    parentLabel: parentLabel.substring(0, 100),
                    prevLabel: prevLabel
                };
            });
        }""")

        print(json.dumps(fields, indent=2))

if __name__ == "__main__":
    inspect_audio_fields()
