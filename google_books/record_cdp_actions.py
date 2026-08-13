"""
record_cdp_actions.py
Attaches to active Google Books Chrome window on port 9222,
listens to all user clicks and inputs in real time, logs them to console & notes/recorded_actions.json!
"""

import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")
os.makedirs(NOTES_DIR, exist_ok=True)
RECORD_LOG = os.path.join(NOTES_DIR, "recorded_user_actions.json")

def record_actions():
    recorded_events = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port 9222: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        print(f"🔴 Live Recording User Actions on: {page.url}")
        print(f"   Saving events to: {RECORD_LOG}")
        print("   👉 Perform your clicks/edits in Chrome now — press Ctrl+C when finished!\n")

        js_listener = """
        () => {
            if (window.__cdp_recorder_active) return;
            window.__cdp_recorder_active = true;

            document.addEventListener('click', (e) => {
                const target = e.target;
                const parent = target.closest('button, a, mat-option, [role="option"], mat-select, mat-chip, mat-form-field, input') || target;
                console.log('🔴 CLICK:', JSON.stringify({
                    type: 'click',
                    tag: parent.tagName,
                    text: (parent.innerText || '').trim().replace(/\\n/g, ' ').substring(0, 100),
                    id: parent.id || target.id || '',
                    class: parent.className || '',
                    placeholder: target.placeholder || ''
                }));
            }, true);

            document.addEventListener('input', (e) => {
                const target = e.target;
                console.log('🔴 INPUT:', JSON.stringify({
                    type: 'input',
                    tag: target.tagName,
                    id: target.id || '',
                    placeholder: target.placeholder || '',
                    value: target.value || target.innerText || ''
                }));
            }, true);
        }
        """

        def on_console(msg):
            txt = msg.text
            if "🔴" in txt:
                print(f"[Recorded Event] {txt}")
                try:
                    payload_str = txt.split("🔴 CLICK: ")[-1].split("🔴 INPUT: ")[-1]
                    data = json.loads(payload_str)
                    data["timestamp"] = time.strftime("%H:%M:%S")
                    recorded_events.append(data)
                    with open(RECORD_LOG, "w", encoding="utf-8") as f:
                        json.dump(recorded_events, f, indent=2, ensure_ascii=False)
                except Exception:
                    pass

        page.evaluate(js_listener)
        page.on("console", on_console)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🛑 Stopped recording. Captured {len(recorded_events)} user actions in {RECORD_LOG}")

if __name__ == "__main__":
    record_actions()

