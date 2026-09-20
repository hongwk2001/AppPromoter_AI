"""
d2d_0_prepare_metadata.py
Generates a single, unified metadata JSON payload per book containing all fields
for Step 1 (Metadata), Step 2 (Details), and Step 3 (Pricing & Rights).
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
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "Tono-Bungay",
        "author_en": "H. G. Wells",
        "author_ko": "H. G. 웰스",
        "publisher": "TKPROF LLC",
        "explicit_content": False,
        "categories": ["Fiction / Classics", "Fiction / Satire", "Fiction / Literary"],
        "keywords_ko": ["토노번게이", "Tono Bungay", "HG웰스", "고전소설", "영국문학", "풍자소설"],
        "keywords_en": ["tono bungay", "hg wells", "classic literature", "satire", "edwardian fiction"],
        "price_usd": "3.99",
        "library_price_usd": "9.99"
    },
    "the_enchanted_april": {
        "title_en": "The Enchanted April",
        "title_ko": "마법에 걸린 4월 (Enchanted April)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "The Enchanted April",
        "author_en": "Elizabeth von Arnim",
        "author_ko": "엘리자베스 폰 아르님",
        "publisher": "TKPROF LLC",
        "explicit_content": False,
        "categories": ["Fiction / Classics", "Fiction / Romance / General", "Fiction / Women's Fiction"],
        "keywords_ko": ["마법에걸린4월", "Enchanted April", "고전소설", "힐링소설", "이탈리아", "로맨스"],
        "keywords_en": ["classic novel", "enchanted april", "elizabeth von arnim", "italy", "romance"],
        "price_usd": "3.99",
        "library_price_usd": "9.99"
    },
    "secret_garden": {
        "title_en": "The Secret Garden",
        "title_ko": "비밀의 화원 (The Secret Garden)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "The Secret Garden",
        "author_en": "Frances Hodgson Burnett",
        "author_ko": "프랜시스 호지슨 버넷",
        "publisher": "TKPROF LLC",
        "explicit_content": False,
        "categories": ["Fiction / Classics", "Juvenile Fiction / Classics", "Fiction / Coming of Age"],
        "keywords_ko": ["비밀의화원", "The Secret Garden", "고전소설", "성장소설", "영국문학"],
        "keywords_en": ["secret garden", "classic literature", "coming of age", "burnett"],
        "price_usd": "3.99",
        "library_price_usd": "9.99"
    },
    "gilgamesh": {
        "title_en": "The Epic of Gilgamesh",
        "title_ko": "길가메시 서사시 (The Epic of Gilgamesh)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "The Epic of Gilgamesh",
        "author_en": "Anonymous",
        "author_ko": "고대 메소포타미아 서사시",
        "publisher": "TKPROF LLC",
        "explicit_content": False,
        "categories": ["Fiction / Classics", "Poetry / Ancient & Classical", "Fiction / Epic"],
        "keywords_ko": ["길가메시서사시", "The Epic of Gilgamesh", "메소포타미아", "고대서사시", "신화"],
        "keywords_en": ["epic of gilgamesh", "mesopotamia", "ancient literature", "mythology"],
        "price_usd": "3.99",
        "library_price_usd": "9.99"
    },
    "blue_castle": {
        "title_en": "The Blue Castle",
        "title_ko": "블루 캐슬 (The Blue Castle)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "The Blue Castle",
        "author_en": "L. M. Montgomery",
        "author_ko": "L. M. 몽고메리",
        "publisher": "TKPROF LLC",
        "explicit_content": False,
        "categories": ["Fiction / Classics", "Fiction / Romance / General", "Fiction / Women's Fiction"],
        "keywords_ko": ["블루캐슬", "TheBlueCastle", "LM몽고메리", "빨강머리앤", "고전소설", "로맨스소설", "힐링소설"],
        "keywords_en": ["blue castle", "lm montgomery", "classic novel", "romance", "canadian literature"],
        "price_usd": "3.99",
        "library_price_usd": "9.99"
    },
    "beowulf": {
        "title_en": "Beowulf",
        "title_ko": "베오울프: 스펙터클 현대 한국어판 (Beowulf)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "Beowulf: Modern Korean Edition",
        "author_en": "Anonymous",
        "author_ko": "작자 미상",
        "publisher": "TKPROF LLC",
        "explicit_content": False,
        "categories": ["Fiction / Classics", "Fiction / Action & Adventure", "Fiction / Fantasy / Action & Adventure"],
        "keywords_ko": ["베오울프", "Beowulf", "고전소설", "신화", "액션판타지", "영웅서사시"],
        "keywords_en": ["beowulf", "classic literature", "epic poem", "heroic fantasy"],
        "price_usd": "3.99",
        "library_price_usd": "9.99"
    },
    "odyssey": {
        "title_en": "The Odyssey",
        "title_ko": "오디세이아 (Odysseia)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "현대인을 위한 모험 서사 판타지",
        "author_en": "Homer",
        "author_ko": "호메로스",
        "publisher": "TKPROF LLC",
        "explicit_content": False,
        "categories": ["Fiction / Classics", "Fiction / Action & Adventure", "Fiction / Epic"],
        "keywords_ko": ["오디세이아", "Odysseia", "호메로스", "그리스신화", "고전문학", "영웅담", "모험소설"],
        "keywords_en": ["the odyssey", "homer", "classic literature", "greek mythology", "epic poem"],
        "price_usd": "5.99",
        "library_price_usd": "11.99"
    },
    "scaramouche_book1": {
        "title_en": "Scaramouche: Book 1 - The Robe",
        "title_ko": "스카라무슈 1: 법의 옷 (Scaramouche)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "프랑스 혁명의 불길 속에서 탄생한 비극과 웃음의 모험 대서사시",
        "author_en": "Rafael Sabatini",
        "author_ko": "라파엘 사바티니",
        "publisher": "TKPROF LLC",
        "explicit_content": False,
        "categories": ["Fiction / Action & Adventure", "Fiction / Historical / General", "Fiction / Classics"],
        "keywords_ko": ["스카라무슈", "Scaramouche", "라파엘사바티니", "프랑스혁명", "역사모험소설", "고전소설", "활극"],
        "keywords_en": ["scaramouche", "rafael sabatini", "french revolution", "swashbuckler", "classic literature"],
        "price_usd": "3.99",
        "library_price_usd": "9.99",
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
        "explicit_content": False,
        "categories": ["Fiction / Action & Adventure", "Fiction / Historical / General", "Fiction / Classics"],
        "keywords_ko": ["스카라무슈", "Scaramouche", "라파엘사바티니", "프랑스혁명", "역사모험소설", "고전소설", "활극"],
        "keywords_en": ["scaramouche", "rafael sabatini", "french revolution", "swashbuckler", "classic literature"],
        "price_usd": "3.99",
        "library_price_usd": "9.99",
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
        "explicit_content": False,
        "categories": ["Fiction / Action & Adventure", "Fiction / Historical / General", "Fiction / Classics"],
        "keywords_ko": ["스카라무슈", "Scaramouche", "라파엘사바티니", "프랑스혁명", "역사모험소설", "고전소설", "활극"],
        "keywords_en": ["scaramouche", "rafael sabatini", "french revolution", "swashbuckler", "classic literature"],
        "price_usd": "3.99",
        "library_price_usd": "9.99",
        "series_title_en": "Scaramouche",
        "series_title_ko": "스카라무슈",
        "volume": "3"
    },
    "dracula_bilingual": {
        "title_en": "Dracula: Bilingual Parallel Edition (English - Korean)",
        "title_ko": "드라큘라 (Dracula) - 영한 대역판 (Bilingual Edition)",
        "subtitle_en": "Bram Stoker's Gothic Masterpiece (A Line-by-Line Parallel Edition for Language Learners)",
        "subtitle_ko": "브램 스토커의 고딕 공포 거작 (영한 대역 / 영어 학습 / 클래식 호러)",
        "author_en": "Bram Stoker",
        "author_ko": "브램 스토커",
        "publisher": "TKPROF LLC",
        "explicit_content": False,
        "categories": ["Fiction / Classics", "Foreign Language Study / Korean", "Fiction / Horror"],
        "keywords_ko": ["드라큘라", "Dracula", "브램스토커", "한영대역", "영한대역", "영어공부", "고전문학", "공포소설"],
        "keywords_en": ["dracula bilingual english korean", "bram stoker classics", "gothic horror vampire", "learn korean reading", "parallel text dual language"],
        "price_usd": "4.99",
        "library_price_usd": "9.99"
    }
}

def resolve_book_path(book_name):
    if os.path.isabs(book_name) and os.path.exists(book_name):
        return book_name, os.path.basename(book_name)
    
    base_name = book_name.split("_")[0] if "_" in book_name else book_name
    candidates = [
        os.path.join(BASE_DIR, book_name),
        os.path.join(r"C:\git_repo\TKprof_book\books", book_name),
        os.path.join(r"C:\git_repo\TKprof_book\books", base_name)
    ]
    for c in candidates:
        if os.path.exists(c):
            return c, book_name
    return None, book_name

def prepare_unified_metadata(book_name, lang="ko"):
    book_path, b_key = resolve_book_path(book_name)
    if not book_path:
        print(f"Error: Could not locate book folder for '{book_name}'")
        return None

    preset = BOOK_PRESETS.get(b_key, {})

    # Resolve text fields based on language
    if lang == "ko":
        title = preset.get("title_ko", b_key.replace("_", " ").title())
        subtitle = preset.get("subtitle_ko", "")
        author = preset.get("author_ko", "TKPROF LLC")
        keywords = preset.get("keywords_ko", [])
    else:
        title = preset.get("title_en", b_key.replace("_", " ").title())
        subtitle = preset.get("subtitle_en", "")
        author = preset.get("author_en", "Anonymous")
        keywords = preset.get("keywords_en", [])

    # Descriptions
    b_num = b_key.split("_")[-1] if "_" in b_key else ""
    full_description = ""
    desc_files = [
        os.path.join(book_path, f"overview_{b_key}_{lang}.txt"),
        os.path.join(book_path, f"overview_{b_num}_{lang}.txt"),
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

    short_description = ""
    short_desc_path = os.path.join(book_path, f"short_description_{lang}.txt")
    if os.path.exists(short_desc_path):
        with open(short_desc_path, "r", encoding="utf-8") as f:
            short_description = f.read().strip()
            
    if not short_description or len(short_description) < 60:
        if full_description:
            paras = [p.strip() for p in full_description.split("\n\n") if p.strip() and not p.startswith("#")]
            combined = " ".join(paras[:2])
            short_description = combined[:390] if len(combined) >= 50 else full_description[:390]

    short_description = short_description[:400]

    # Files
    epub_candidates = [
        os.path.join(book_path, f"{b_key}_{lang}_v2.epub"),
        os.path.join(book_path, f"the_{b_key}_{lang}_v2.epub"),
        os.path.join(book_path, f"{b_key}_{lang}.epub"),
        os.path.join(book_path, f"the_{b_key}_{lang}.epub"),
        os.path.join(book_path, f"{b_key}.epub"),
        os.path.join(book_path, f"the_{b_key}.epub"),
    ]
    epub_path = ""
    for e_cand in epub_candidates:
        if os.path.exists(e_cand):
            epub_path = e_cand
            break

    cover_path = ""
    cover_candidates = [
        os.path.join(book_path, f"cover_{b_num}_{lang}.jpg"),
        os.path.join(book_path, f"cover_{b_num}_final.jpg"),
        os.path.join(book_path, f"cover_{b_num}.jpg"),
        os.path.join(book_path, f"cover_{b_num}.png"),
        os.path.join(book_path, f"cover_{lang}.jpg"),
        os.path.join(book_path, f"cover_{lang}.png"),
        os.path.join(book_path, "cover.jpg"),
        os.path.join(book_path, "cover.png")
    ]
    for c in cover_candidates:
        if os.path.exists(c):
            cover_path = c
            break

    # Build Unified Metadata Structure
    metadata = {
        "book_id": b_key,
        "language_code": lang,
        "language_name": "Korean" if lang == "ko" else "English",
        "step1_metadata": {
            "title": title,
            "subtitle": subtitle,
            "author": author,
            "publisher": preset.get("publisher", "TKPROF LLC"),
            "explicit_content": preset.get("explicit_content", False),
            "search_terms": keywords,
            "bisac_categories": preset.get("categories", ["Fiction / Classics", "Fiction / Satire"]),
            "cover_image_path": os.path.abspath(cover_path) if os.path.exists(cover_path) else "",
            "cover_exists": os.path.exists(cover_path)
        },
        "step2_details": {
            "epub_path": os.path.abspath(epub_path) if os.path.exists(epub_path) else "",
            "epub_exists": os.path.exists(epub_path),
            "short_description": short_description[:400],
            "full_description_text": full_description,
            "contributors": [
                {"name": "TKPROF LLC", "role": "Translator"},
                {"name": "TKPROF LLC", "role": "Editor"}
            ],
            "use_free_d2d_isbn": True
        },
        "step3_pricing": {
            "digital_price_usd": preset.get("price_usd", "3.99"),
            "library_price_usd": preset.get("library_price_usd", "9.99"),
            "remember_store_preferences": True,
            "promotion_price_mode": "normal",
            "target_stores": {
                "enable_all_supported": True,
                "skip_unsupported_language_stores": True,
                "custom_store_states": {
                    "Barnes & Noble": False,
                    "Kobo": True,
                    "Apple": True,
                    "Tolino": True,
                    "Vivlio": True,
                    "Smashwords": True,
                    "Gardners": False,
                    "Bookshop.org": True,
                    "Fable": True,
                    "Everand": True,
                    "OverDrive": True,
                    "cloudLibrary": True,
                    "BorrowBox": True
                }
            }
        }
    }

    out_file = os.path.join(NOTES_DIR, f"d2d_metadata_{b_key}_{lang}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated Unified Single-File Metadata: {out_file}")
    print(f"  Book: {title}")
    print(f"  EPUB Exists: {metadata['step2_details']['epub_exists']}")
    print(f"  Cover Exists: {metadata['step1_metadata']['cover_exists']}\n")
    return metadata

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Single Unified Metadata JSON per Book")
    parser.add_argument("--book", type=str, required=True, help="Book key or folder path")
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    args = parser.parse_args()

    prepare_unified_metadata(args.book, args.lang)
