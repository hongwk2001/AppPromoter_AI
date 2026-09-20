import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def fix_contributors(port=9222):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]

        print(f"Connected to page: {page.url} ({page.title()})\n")

        # 1. Update Contributor 1 (Author) Bio if needed
        editors = page.locator('div.ql-editor')
        print(f"Found {editors.count()} rich text editors on page.")

        bio_author = "《베오울프》(Beowulf)는 8세기~11세기경 고대 영어로 작성된 영문학 최선두의 고대 서사시로, 작자는 미상이나 인류 문학사에서 영웅 서사시의 원형으로 평가받습니다."
        bio_narrator = "TKPROF LLC는 고전 문학의 현대화 및 오디오북 퍼블리싱 전문 팀입니다. 본 오디오북 개정판은 고대 영문학 대서사시 《베오울프》 원작을 현대 한국어 독자와 오디오북 청취 환경에 맞춰 정교하게 편역 및 낭독 제작했습니다: 1) 번역 방식: 딱딱하고 장황한 고어 직역을 벗어나 현대 웹소설의 스펙터클한 문법과 속도감 넘치는 현대 구어체로 완판 재번역했습니다. 2) 낭독 및 음성 연출: 성우 및 AI 내레이션 기술을 조합하여 장면별 서사적 긴장감, 전투 몰입감, 문장 호흡을 오디오 청취에 최적화하여 연출했습니다. 3) 생략 없는 완판 서사 구조를 보존하여 오디오북 청취자에게 최고의 몰입감을 제공합니다."

        if editors.count() > 0:
            editors.nth(0).evaluate("(el, txt) => { el.innerHTML = '<p>' + txt + '</p>'; el.dispatchEvent(new Event('input', {bubbles:true})); }", bio_author)
            print("  ✓ Set Contributor 1 (Author) Bio")

        if editors.count() > 1:
            editors.nth(1).evaluate("(el, txt) => { el.innerHTML = '<p>' + txt + '</p>'; el.dispatchEvent(new Event('input', {bubbles:true})); }", bio_narrator)
            print("  ✓ Set Contributor 2 (Narrator) Bio")

        if editors.count() > 2:
            # Also fill 3rd editor if present for Translator
            editors.nth(2).evaluate("(el, txt) => { el.innerHTML = '<p>' + txt + '</p>'; el.dispatchEvent(new Event('input', {bubbles:true})); }", bio_narrator)
            print("  ✓ Set Contributor 3 (Translator) Bio")

        print("\n✨ Contributors page clean update complete!")

if __name__ == "__main__":
    fix_contributors()
