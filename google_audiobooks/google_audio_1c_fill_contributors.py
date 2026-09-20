"""
google_audio_1c_fill_contributors.py
Populates the Contributors sub-tab for Google Books Audiobook Partner Center entries over CDP port 9222.
"""

import os
import sys
import json
import time
import argparse
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

CONTRIBUTOR_PRESETS = {
    "blue_castle": [
        {
            "name": "L. M. 몽고메리",
            "role": "Author",
            "bio": "루시 모드 몽고메리(Lucy Maud Montgomery, 1874~1942)는 세계적인 명작 『빨강 머리 앤(Anne of Green Gables)』과 성인 독자들을 위한 힐링 로맨스 거작 『블루 캐슬(The Blue Castle)』을 집필한 캐나다의 대표적인 클래식 소설가입니다. 아름다운 자연 묘사와 삶의 용기를 전하는 당찬 여성 캐릭터들로 전 세계 수많은 독자들에게 사랑받고 있습니다."
        },
        {"name": "TKPROF AI", "role": "Narrator"},
        {"name": "TKPROF LLC", "role": "Publisher"}
    ],
    "beowulf": [
        {
            "name": "작자 미상",
            "role": "Author",
            "bio": "《베오울프》(Beowulf)는 8세기~11세기경 고대 영어로 작성된 영문학 최선두의 고대 서사시로, 작자는 미상이나 인류 문학사에서 영웅 서사시의 원형으로 평가받습니다."
        },
        {
            "name": "TKPROF LLC",
            "role": "Narrator",
            "bio": "TKPROF LLC는 고전 문학의 현대화 및 오디오북 퍼블리싱 전문 팀입니다. 본 오디오북 개정판은 고대 영문학 대서사시 《베오울프》 원작을 현대 한국어 독자와 오디오북 청취 환경에 맞춰 정교하게 편역 및 낭독 제작했습니다: 1) 번역 방식: 딱딱하고 장황한 고어 직역을 벗어나 현대 웹소설의 스펙터클한 문법과 속도감 넘치는 현대 구어체로 완판 재번역했습니다. 2) 낭독 및 음성 연출: 성우 및 AI 내레이션 기술을 조합하여 장면별 서사적 긴장감, 전투 몰입감, 문장 호흡을 오디오 청취에 최적화하여 연출했습니다. 3) 생략 없는 완판 서사 구조를 보존하여 오디오북 청취자에게 최고의 몰입감을 제공합니다."
        }
    ],
    "dracula": [
        {
            "name": "브람 스토커",
            "role": "Author",
            "bio": "브람 스토커(Bram Stoker, 1847~1912)는 세계 소설사에서 뱀파이어 문학의 최고 금자탑으로 평가받는 고딕 공포 명작 《드라큘라》(Dracula, 1897)를 집필한 아일랜드 출신의 대표적인 소설가입니다."
        },
        {
            "name": "Aiden (English), SunHi (Korean)",
            "role": "Narrator",
            "bio": "본 오디오북은 원어민 영어 내레이터 Aiden과 한국어 내레이터 SunHi의 정교한 문장별 이중 언어(Bilingual) 교차 낭독으로 제작되었습니다."
        }
    ]
}

def load_audio_metadata(book_name, lang="ko"):
    meta_path = os.path.join(NOTES_DIR, f"google_audio_metadata_{book_name}_{lang}.json")
    if not os.path.exists(meta_path):
        from google_audio_0_prepare_metadata import prepare_audio_metadata
        return prepare_audio_metadata(book_name, lang)
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def fill_audio_contributors(book_name, lang="ko", port=9222):
    data = load_audio_metadata(book_name, lang)
    if not data:
        print("Error: Could not load Audiobook metadata.")
        return

    contributors = CONTRIBUTOR_PRESETS.get(book_name, [
        {"name": data["book_info"]["author"], "role": "Author"},
        {"name": data["book_info"].get("narrator", "TKPROF AI"), "role": "Narrator"}
    ])

    print(f"\n📋 Filling Google Books Audiobook Contributors for: {book_name} ({lang.upper()})")
    print(f"  Contributors: {contributors}\n")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"Error: Could not connect to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page: {page.url} ({page.title()})")

        # Dismiss any open Angular Material overlays (backdrops, dropdowns)
        page.keyboard.press("Escape")
        time.sleep(0.5)

        # 1. Switch to Contributors sub-tab if needed
        if "info/contributors" not in page.url:
            contrib_tab = page.locator('a[href*="info/contributors"], a:has-text("Contributors"), span:has-text("Contributors"), div[role="tab"]:has-text("Contributors")')
            if contrib_tab.count() > 0:
                print("➡️ Switching to Contributors tab...")
                contrib_tab.first.click(force=True)
                time.sleep(1.5)

        # 2. Add each contributor
        for idx, contrib in enumerate(contributors):
            name = contrib.get("name", "")
            role = contrib.get("role", "Author")

            # Click 'Add a contributor' if row doesn't exist
            name_inps = page.locator('input[placeholder*="Name"], input[aria-label*="Name"]')
            if name_inps.count() <= idx:
                add_btn = page.locator('button:has-text("Add a contributor"), [role="button"]:has-text("Add a contributor")').first
                if add_btn.count() > 0 and add_btn.is_visible():
                    add_btn.click()
                    time.sleep(1)

            # Target Name input
            name_inps = page.locator('input[placeholder*="Name"], input[aria-label*="Name"]')
            target_inp = name_inps.nth(idx) if name_inps.count() > idx else name_inps.last
            if target_inp.count() > 0:
                target_inp.focus()
                target_inp.fill(name)
                print(f"  ✓ Filled Name [{idx+1}]: {name}")
                time.sleep(0.5)

            # Target Role mat-select
            role_selects = page.locator('mat-select')
            target_select = role_selects.nth(idx) if role_selects.count() > idx else role_selects.last
            if target_select.count() > 0:
                target_select.click()
                time.sleep(0.5)
                # Select role option
                role_opt = page.locator(f'mat-option:has-text("{role}")')
                if role_opt.count() > 0:
                    role_opt.first.click()
                    print(f"  ✓ Selected Role [{idx+1}]: {role}")
                else:
                    # Fallback to first option
                    page.keyboard.press("Enter")

            # Target Bio field (textarea or contenteditable editor, excluding hidden ql-clipboard)
            bio = contrib.get("bio", "")
            if bio:
                bio_inps = page.locator('textarea, div.ql-editor:not(.ql-clipboard)')
                visible_bios = [bio_inps.nth(i) for i in range(bio_inps.count()) if bio_inps.nth(i).is_visible()]
                if idx < len(visible_bios):
                    target_bio = visible_bios[idx]
                    target_bio.click()
                    tag_name = target_bio.evaluate("el => el.tagName")
                    if tag_name == "TEXTAREA":
                        target_bio.fill(bio)
                    else:
                        target_bio.evaluate("(el, txt) => { el.innerText = txt; el.dispatchEvent(new Event('input', {bubbles:true})); }", bio)
                    print(f"  ✓ Filled Biography [{idx+1}]: {bio[:40]}...")
                    time.sleep(0.5)

        print("\n✨ Audiobook Contributors Autofill Finished! (Form populated — Browser paused for your review)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill Google Play Books Audiobook Contributors")
    parser.add_argument("--book", type=str, required=True, help="Book key or folder path")
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    args = parser.parse_args()

    fill_audio_contributors(args.book, args.lang)
