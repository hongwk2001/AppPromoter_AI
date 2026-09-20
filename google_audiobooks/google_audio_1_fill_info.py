"""
google_audio_1_fill_info.py
Populates Tab 1 (About the book) for Google Books Audiobook Partner Center entries over CDP port 9222.
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

def load_audio_metadata(book_name, lang="ko"):
    meta_path = os.path.join(NOTES_DIR, f"google_audio_metadata_{book_name}_{lang}.json")
    if not os.path.exists(meta_path):
        from google_audio_0_prepare_metadata import prepare_audio_metadata
        return prepare_audio_metadata(book_name, lang)
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def fill_audio_info(book_name, lang="ko", port=9222):
    data = load_audio_metadata(book_name, lang)
    if not data:
        print("Error: Could not load Audiobook metadata.")
        return

    info = data["book_info"]
    print(f"\n📋 Filling Google Books Audiobook Tab 1 (About the book) for: {info['title']} ({lang.upper()})")
    print(f"  Author:     {info['author']}")
    print(f"  Publisher:  {info['publisher']}")
    print(f"  Narrator:   {info.get('narrator', 'TKPROF AI')}\n")

    # Format description into clean HTML paragraphs
    desc_raw = info.get("description", "")
    paragraphs = [p.strip().replace("\n", "<br>") for p in desc_raw.split("\n\n") if p.strip()]
    desc_html = "".join([f"<p>{p}</p>" for p in paragraphs])

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        # Switch to 'About the book' main tab if needed
        if "/info" not in page.url:
            info_tab = page.locator('a[href*="info"], a:has-text("About the book"), span:has-text("About the book")')
            if info_tab.count() > 0:
                print("➡️ Switching to 'About the book' tab...")
                info_tab.first.click(force=True)
                page.wait_for_timeout(1500)

        print(f"Active Tab: {page.url} ({page.title()})")

        js_fill = """
        (data) => {
            const filled = [];

            function setVal(input, val) {
                if (!input || val === undefined || val === null) return false;
                input.focus();
                input.value = val;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                input.dispatchEvent(new Event('blur', { bubbles: true }));
                return true;
            }

            // 1. Fill Title
            const inputs = Array.from(document.querySelectorAll('input, textarea'));
            const titleInp = inputs.find(i => {
                const p = i.closest('mat-form-field') || i.parentElement;
                const txt = (p ? p.innerText : '').toLowerCase();
                return txt.includes('title') && !txt.includes('subtitle');
            }) || inputs[0];

            if (setVal(titleInp, data.title)) filled.push('Title');

            // 2. Add Subtitle if present
            if (data.subtitle) {
                const subBtns = Array.from(document.querySelectorAll('button, a')).filter(b => b.innerText.includes('Subtitle'));
                if (subBtns.length > 0) {
                    subBtns[0].click();
                }
                setTimeout(() => {
                    const subInp = inputs.find(i => {
                        const p = i.closest('mat-form-field') || i.parentElement;
                        return (p ? p.innerText : '').toLowerCase().includes('subtitle');
                    });
                    if (subInp) setVal(subInp, data.subtitle);
                }, 400);
            }

            // 3. Description (Rich Text Editor or Textarea)
            const editor = document.querySelector('.ql-editor, [contenteditable="true"]');
            if (editor && data.desc_html) {
                editor.focus();
                editor.innerHTML = data.desc_html;
                editor.dispatchEvent(new Event('input', { bubbles: true }));
                filled.push('Description (HTML)');
            } else {
                const descArea = document.querySelector('textarea');
                if (descArea && setVal(descArea, data.description)) filled.push('Description');
            }

            return filled;
        }
        """

        res = page.evaluate(js_fill, {
            "title": info["title"],
            "subtitle": info.get("subtitle", ""),
            "author": info["author"],
            "publisher": info.get("publisher", "TKPROF LLC"),
            "description": desc_raw,
            "desc_html": desc_html
        })

        # Native Playwright actions for Subtitle button & Language selection
        if info.get("subtitle"):
            sub_btn = page.locator('button:has-text("Add a subtitle"), a:has-text("Add a subtitle"), [role="button"]:has-text("Add a subtitle")')
            if sub_btn.count() > 0:
                sub_btn.first.click()
                page.wait_for_timeout(600)
                sub_inp = page.locator('input[aria-label*="Subtitle"], mat-form-field:has-text("Subtitle") input')
                if sub_inp.count() > 0:
                    sub_inp.first.fill(info["subtitle"])
                    print(f"  ✓ Filled Subtitle: {info['subtitle']}")

        # Select Language (Korean)
        lang_sel = page.locator('mat-select:has-text("Language"), mat-select[aria-label*="Language"]')
        if lang_sel.count() > 0:
            lang_sel.first.click()
            page.wait_for_timeout(600)
            kor_opt = page.locator('mat-option:has-text("Korean"), mat-option:has-text("한국어")')
            if kor_opt.count() > 0:
                kor_opt.first.click()
                print("  ✓ Selected Language: Korean")

        # Fill Audio Duration (HH:MM:SS)
        dur_val = info.get("duration", "03:05:04")
        dur_inp = page.locator('input[placeholder*="HH:MM:SS" i], input[placeholder*="hh:mm:ss" i], mat-form-field:has-text("Duration") input, mat-form-field:has-text("길이") input, #mat-input-8')
        if dur_inp.count() > 0:
            dur_inp.first.fill(dur_val)
            print(f"  ✓ Filled Audio Duration: {dur_val}")

        print(f"  ✓ Autofilled fields: {res}")
        print("\n✨ Audiobook Tab 1 Autofill Finished! (Form populated — Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill Google Play Books Audiobook Tab 1 (About the book)")
    parser.add_argument("--book", type=str, required=True, help="Book key or folder path")
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    args = parser.parse_args()

    fill_audio_info(args.book, args.lang)
