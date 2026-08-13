"""
google_0_prepare_metadata.py
Generates a single, unified JSON metadata payload per book formatted for
Google Books Partner Center (play.google.com/books/publish/).
"""

import os
import sys
import json
import argparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")
os.makedirs(NOTES_DIR, exist_ok=True)

BOOK_PRESETS = {
    "tono_bungay": {
        "title_en": "Tono-Bungay",
        "title_ko": "토노 번게이 (Tono-Bungay)",
        "subtitle_en": "H. G. Wells' Classic Novel of Ambition and the Ultimate Snake-Oil Scam",
        "subtitle_ko": "가짜 만병통치약으로 이룬 헛된 자본주의 제국과 덧없는 야망의 대서사시",
        "author_en": "H. G. Wells",
        "author_ko": "H. G. 웰스",
        "publisher": "TKPROF LLC",
        "categories": ["FICTION / Classics", "FICTION / Satire"],
        "price_usd": "3.99",
        "page_count": "411"
    },
    "the_enchanted_april": {
        "title_en": "The Enchanted April",
        "title_ko": "마법에 걸린 4월 (Enchanted April)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "The Enchanted April",
        "author_en": "Elizabeth von Arnim",
        "author_ko": "엘리자베스 폰 아르님",
        "publisher": "TKPROF LLC",
        "categories": ["FICTION / Classics", "FICTION / Romance / General"],
        "price_usd": "3.99"
    },
    "secret_garden": {
        "title_en": "The Secret Garden",
        "title_ko": "비밀의 화원 (The Secret Garden)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "The Secret Garden",
        "author_en": "Frances Hodgson Burnett",
        "author_ko": "프랜시스 호지슨 버넷",
        "publisher": "TKPROF LLC",
        "categories": ["FICTION / Classics", "JUVENILE FICTION / Classics"],
        "price_usd": "3.99"
    },
    "gilgamesh": {
        "title_en": "The Epic of Gilgamesh",
        "title_ko": "길가메시 서사시 (The Epic of Gilgamesh)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "The Epic of Gilgamesh",
        "author_en": "Anonymous",
        "author_ko": "고대 메소포타미아 서사시",
        "publisher": "TKPROF LLC",
        "categories": ["FICTION / Classics", "POETRY / Ancient & Classical"],
        "price_usd": "3.99"
    },
    "odyssey": {
        "title_en": "The Odyssey",
        "title_ko": "오디세이아 (Odysseia)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "현대인을 위한 모험 서사 판타지",
        "author_en": "Homer",
        "author_ko": "호메로스",
        "publisher": "TKPROF LLC",
        "categories": ["FICTION / Classics", "FICTION / Action & Adventure"],
        "price_usd": "3.99"
    },
    "scaramouche_book1": {
        "title_en": "Scaramouche: Book 1 - The Robe",
        "title_ko": "스카라무슈 1: 법의 옷 (Scaramouche)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "프랑스 혁명의 불길 속에서 탄생한 비극과 웃음의 모험 대서사시",
        "author_en": "Rafael Sabatini",
        "author_ko": "라파엘 사바티니",
        "publisher": "TKPROF LLC",
        "categories": ["FICTION / Action & Adventure", "FICTION / Historical / General", "FICTION / Classics"],
        "price_usd": "3.99",
        "series_title_en": "Scaramouche",
        "series_title_ko": "스카라무슈",
        "volume": "1"
    },
    "scaramouche_book2": {
        "title_en": "Scaramouche: Book 2 - The Buskin",
        "title_ko": "스카라무슈 2: 배우의 신발 (Scaramouche)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "무대 위의 배우에서 혁명의 정점으로",
        "author_en": "Rafael Sabatini",
        "author_ko": "라파엘 사바티니",
        "publisher": "TKPROF LLC",
        "categories": ["FICTION / Action & Adventure", "FICTION / Historical / General", "FICTION / Classics"],
        "price_usd": "3.99",
        "series_title_en": "Scaramouche",
        "series_title_ko": "스카라무슈",
        "volume": "2"
    },
    "scaramouche_book3": {
        "title_en": "Scaramouche: Book 3 - The Sword",
        "title_ko": "스카라무슈 3: 검의 언어 (Scaramouche)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "장엄한 운명의 결투와 마침내 밝혀지는 진실",
        "author_en": "Rafael Sabatini",
        "author_ko": "라파엘 사바티니",
        "publisher": "TKPROF LLC",
        "categories": ["FICTION / Action & Adventure", "FICTION / Historical / General", "FICTION / Classics"],
        "price_usd": "3.99",
        "series_title_en": "Scaramouche",
        "series_title_ko": "스카라무슈",
        "volume": "3"
    },
    "dracula_bilingual": {
        "title_en": "Dracula: Bilingual Parallel Edition (English - Korean)",
        "title_ko": "드라큘라 (Dracula) - 한영 대역판 (Bilingual Edition)",
        "subtitle_en": "Bram Stoker's Gothic Masterpiece (A Line-by-Line Parallel Edition for Language Learners)",
        "subtitle_ko": "브램 스토커의 고딕 공포 거작 (영한 대역 / 영어 학습 / 클래식 호러)",
        "author_en": "Bram Stoker",
        "author_ko": "브램 스토커",
        "publisher": "TKPROF LLC",
        "categories": ["FICTION / Classics", "FOREIGN LANGUAGE STUDY / Korean", "FICTION / Horror"],
        "price_usd": "4.99",
        "page_count": "650"
    }
}

def resolve_book_path(book_name):
    if os.path.isabs(book_name) and os.path.exists(book_name):
        return book_name, os.path.basename(book_name)
    
    base_name = book_name.split("_")[0] if "_" in book_name else book_name
    candidates = [
        os.path.join(os.path.dirname(BASE_DIR), "draft2digital", book_name),
        os.path.join(r"C:\git_repo\TKprof_book\books", book_name),
        os.path.join(r"C:\git_repo\TKprof_book\books", base_name)
    ]
    for c in candidates:
        if os.path.exists(c):
            return c, book_name
    return None, book_name

def prepare_google_metadata(book_name, lang="ko"):
    book_path, b_key = resolve_book_path(book_name)
    if not book_path:
        print(f"Error: Could not locate book directory for '{book_name}'")
        return None

    preset = BOOK_PRESETS.get(b_key, {})

    if lang == "ko":
        title = preset.get("title_ko", b_key.replace("_", " ").title())
        subtitle = preset.get("subtitle_ko", "")
        author = preset.get("author_ko", "TKPROF LLC")
    else:
        title = preset.get("title_en", b_key.replace("_", " ").title())
        subtitle = preset.get("subtitle_en", "")
        author = preset.get("author_en", "Anonymous")

    full_description = ""
    b_num = b_key.replace("scaramouche_book", "")
    desc_files = [
        os.path.join(book_path, f"overview_book{b_num}_{lang}.txt"),
        os.path.join(book_path, f"overview_{b_key}_{lang}.txt"),
        os.path.join(book_path, f"overview_{lang}.txt"),
        os.path.join(book_path, f"introduction_{lang}.txt"),
        os.path.join(book_path, f"copyright_{lang}.txt"),
        os.path.join(book_path, "metadata.md")
    ]
    for path in desc_files:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                full_description = f.read().strip()
                break

    epub_path = os.path.join(book_path, f"{b_key}_{lang}.epub")
    if not os.path.exists(epub_path):
        alt_epub = os.path.join(book_path, f"{b_key}.epub")
        if os.path.exists(alt_epub):
            epub_path = alt_epub

    cover_path = ""
    cover_candidates = [
        os.path.join(book_path, f"cover_{lang}.jpg"),
        os.path.join(book_path, f"cover_{lang}.png"),
        os.path.join(book_path, "cover.jpg"),
        os.path.join(book_path, "cover.png")
    ]
    for c in cover_candidates:
        if os.path.exists(c):
            cover_path = c
            break

    metadata = {
        "book_id": b_key,
        "language_code": lang,
        "language_name": "Korean" if lang == "ko" else "English",
        "tab1_about_the_book": {
            "title": title,
            "subtitle": subtitle,
            "book_identifier": "",
            "language": "Korean" if lang == "ko" else "English",
            "publisher": preset.get("publisher", "TKPROF LLC"),
            "format": "Ebook",
            "page_count": preset.get("page_count", "350"),
            "release_date": "2026-08-12",
            "publication_date": "2026-08-12",
            "minimum_age": "",
            "maximum_age": "",
            "mature_audience": False,
            "description_text": full_description
        },
        "tab2_genres": {
            "bisac_categories": preset.get("categories", ["FICTION / Classics", "FICTION / Satire"])
        },
        "tab3_contributors": [
            {
                "name": author,
                "role": "Author",
                "bio": (
                    "호머(호메로스, Homeros)는 고대 그리스의 대표적인 대서사시인으로, 인류 문학사에서 가장 위대한 서사시로 꼽히는 《일리아스》와 《오디세이아》의 작가입니다."
                    if "odyssey" in b_key else
                    "라파엘 사바티니(Rafael Sabatini, 1875~1950)는 <스카라무슈>(Scaramouche), <캡틴 블러드>(Captain Blood) 등의 명작을 남긴 이탈리아 출신의 세계적인 영국 모험·역사소설가입니다."
                    if "scaramouche" in b_key else
                    "브램 스토커(Bram Stoker, 1847~1912)는 세계 소설사에서 뱀파이어 문학의 최고 금자탑으로 평가받는 고딕 공포 명작 《드라큘라》(Dracula, 1897)를 집필한 아일랜드 출신의 대표적인 소설가입니다."
                    if "dracula" in b_key else
                    "H. G. 웰스(Herbert George Wells, 1866~1946)는 쥘 베른과 함께 '현대 과학소설의 아버지'로 불리는 영국의 대표적인 문학가이자 사회비평가입니다."
                )
            },
            {
                "name": "TKPROF LLC",
                "role": "Translator",
                "bio": (
                    "TKPROF LLC는 고전 문학의 현대화 및 eBook/오디오북 퍼블리싱 전문 팀입니다. 본 현대어 개정판은 라파엘 사바티니(Rafael Sabatini)의 원작을 바탕으로 현대 독자와 TTS 청취 환경에 최적화하여 편역했습니다: 1) 장황한 19세기 문어체 문장을 현대적 구어체 소설 스타일로 다듬었습니다. 2) TTS 음성 읽기 환경에 맞춰 문장 호흡과 대화 흐름을 조절했습니다. 3) 프랑스 혁명기의 역사 용어와 펜싱·극단 고유 명사를 한국어 독자에게 알기 쉽게 다듬었습니다. 4) 완판 서사 구조를 생략 없이 보존했습니다."
                    if "scaramouche" in b_key else
                    "TKPROF LLC는 고전 문학의 현대화 및 한영 대역/이중언어(Bilingual) eBook 퍼블리싱 전문 팀입니다. 본 한영 대역 개정판은 브램 스토커(Bram Stoker)의 1897년 무삭제 원문과 현대 한국어 번역을 단락 대 단락(Line-by-Line Parallel)으로 정밀 배치하여, 영어 학습자, ESL 독자, 고전 문학 팬들이 원문과 번역문을 직관적으로 대조하며 감상할 수 있도록 최적화 제작되었습니다."
                    if "dracula" in b_key else
                    "TKPROF LLC는 고전 문학의 현대화 및 eBook/오디오북 퍼블리싱 전문 팀입니다. 본 현대어 개정판은 새뮤얼 버틀러(Samuel Butler)의 원작 서사시를 바탕으로 현대 독자와 TTS 청취 환경에 최적화하여 편역했습니다: 1) 장황한 고어 문장을 현대적 구어체 소설 스타일로 다듬었습니다. 2) TTS 음성 읽기 환경에 맞춰 문장 호흡과 대화 흐름을 조절했습니다. 3) 로마 신화 표기(울리세스, 미네르바 등)를 친숙한 그리스 신화 표기(오디세우스, 아테나 등)로 통일했습니다. 4) 완판 서사 구조를 생략 없이 보존했습니다."
                )
            }
        ],
        "tab4_series": {
            "series_title": "",
            "volume_number": ""
        },
        "tab5_settings": {
            "enable_drm": True,
            "preview_percentage": "20"
        },
        "files": {
            "epub_path": os.path.abspath(epub_path) if os.path.exists(epub_path) else "",
            "epub_exists": os.path.exists(epub_path),
            "cover_path": os.path.abspath(cover_path) if os.path.exists(cover_path) else "",
            "cover_exists": os.path.exists(cover_path)
        },
        "pricing": {
            "price_usd": preset.get("price_usd", "3.99"),
            "currency": "USD",
            "world_rights": True,
            "territories": ["WORLD"]
        }
    }

    out_file = os.path.join(NOTES_DIR, f"google_metadata_{b_key}_{lang}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Prepared Google Books Single Metadata File: {out_file}")
    print(f"  Title: {title}")
    print(f"  Author: {author}")
    print(f"  EPUB Exists: {metadata['files']['epub_exists']}")
    print(f"  Cover Exists: {metadata['files']['cover_exists']}\n")
    return metadata

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare Google Books Metadata JSON")
    parser.add_argument("--book", type=str, required=True)
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    args = parser.parse_args()

    prepare_google_metadata(args.book, args.lang)
