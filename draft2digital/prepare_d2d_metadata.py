"""
prepare_d2d_metadata.py
Prepares and formats structured JSON metadata and absolute file paths
for a specified book and language edition for Draft2Digital automated publishing.
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

# Preset metadata defaults for books in this repository
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
        "content_rating_text": "My book does NOT contain content inappropriate for minors. It is intended for a general audience.",
        "categories": ["Fiction / Classics", "Fiction / Satire", "Fiction / Literary"],
        "keywords_ko": ["토노번게이", "Tono Bungay", "HG웰스", "고전소설", "영국문학", "풍자소설"],
        "keywords_en": ["tono bungay", "hg wells", "classic literature", "satire", "edwardian fiction"],
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
        "content_rating_text": "My book does NOT contain content inappropriate for minors. It is intended for a general audience.",
        "categories": ["Fiction / Classics", "Fiction / Romance / General", "Fiction / Women's Fiction"],
        "keywords_ko": ["마법에걸린4월", "Enchanted April", "고전소설", "힐링소설", "이탈리아", "로맨스"],
        "keywords_en": ["classic novel", "enchanted april", "elizabeth von arnim", "italy", "romance"],
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
        "content_rating_text": "My book does NOT contain content inappropriate for minors. It is intended for a general audience.",
        "categories": ["Fiction / Classics", "Juvenile Fiction / Classics", "Fiction / Coming of Age"],
        "keywords_ko": ["비밀의화원", "The Secret Garden", "고전소설", "성장소설", "영국문학"],
        "keywords_en": ["secret garden", "classic literature", "coming of age", "burnett"],
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
        "content_rating_text": "My book does NOT contain content inappropriate for minors. It is intended for a general audience.",
        "categories": ["Fiction / Classics", "Poetry / Ancient & Classical", "Fiction / Epic"],
        "keywords_ko": ["길가메시서사시", "The Epic of Gilgamesh", "메소포타미아", "고대서사시", "신화"],
        "keywords_en": ["epic of gilgamesh", "mesopotamia", "ancient literature", "mythology"],
    },
    "beowulf": {
        "title_en": "Beowulf: Spectacular Modern English Edition",
        "title_ko": "베오울프: 스펙터클 현대 한국어판 (Beowulf)",
        "subtitle_en": "Modern English Edition",
        "subtitle_ko": "Beowulf: Modern Korean Edition",
        "author_en": "Anonymous",
        "author_ko": "작자 미상",
        "publisher": "TKPROF LLC",
        "explicit_content": False,
        "content_rating_text": "My book does NOT contain content inappropriate for minors. It is intended for a general audience.",
        "categories": ["Fiction / Classics", "Fiction / Action & Adventure", "Fiction / Fantasy / Action & Adventure"],
        "keywords_ko": ["베오울프", "Beowulf", "고전소설", "신화", "액션판타지", "영웅서사시"],
        "keywords_en": ["beowulf", "classic literature", "action fantasy", "epic poetry"],
    }
}

def prepare_payload(book_name, lang="ko"):
    book_path = os.path.join(BASE_DIR, book_name)
    if not os.path.exists(book_path):
        print(f"Error: Book directory not found: {book_path}")
        return None

    preset = BOOK_PRESETS.get(book_name, {})
    
    # 1. Resolve Title & Subtitle
    if lang == "ko":
        title = preset.get("title_ko", book_name.replace("_", " ").title())
        subtitle = preset.get("subtitle_ko", "")
        author = preset.get("author_ko", "작자 미상")
        keywords = preset.get("keywords_ko", [])
    else:
        title = preset.get("title_en", book_name.replace("_", " ").title())
        subtitle = preset.get("subtitle_en", "")
        author = preset.get("author_en", "Anonymous")
        keywords = preset.get("keywords_en", [])

    # 2. Resolve Description
    description_text = ""
    desc_candidates = [
        os.path.join(book_path, f"overview_{lang}.txt"),
        os.path.join(book_path, f"introduction_{lang}.txt"),
        os.path.join(book_path, f"copyright_{lang}.txt"),
        os.path.join(book_path, "metadata.md")
    ]
    for path in desc_candidates:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                description_text = f.read().strip()
                break

    # 3. Resolve Files
    epub_candidates = [
        os.path.join(book_path, f"{book_name}_{lang}_v2.epub"),
        os.path.join(book_path, f"{book_name}_{lang}.epub"),
        os.path.join(book_path, f"{book_name}.epub")
    ]
    epub_path = ""
    for e_path in epub_candidates:
        if os.path.exists(e_path):
            epub_path = e_path
            break

    cover_candidates = [
        os.path.join(book_path, f"cover_{lang}.jpg"),
        os.path.join(book_path, f"cover_{lang}.png"),
        os.path.join(book_path, "cover.jpg"),
        os.path.join(book_path, "cover.png"),
        os.path.join(book_path, "images", "cover.jpg")
    ]
    cover_path = ""
    for c_path in cover_candidates:
        if os.path.exists(c_path):
            cover_path = c_path
            break

    payload = {
        "book": book_name,
        "language": "Korean" if lang == "ko" else "English",
        "language_code": lang,
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "publisher": preset.get("publisher", "TKPROF LLC"),
        "explicit_content": preset.get("explicit_content", False),
        "content_rating_text": preset.get("content_rating_text", "My book does NOT contain content inappropriate for minors. It is intended for a general audience."),
        "description": description_text,
        "categories": preset.get("categories", ["Fiction / Classics", "Fiction / Satire", "Fiction / Literary"]),
        "keywords": keywords,
        "epub_path": os.path.abspath(epub_path) if os.path.exists(epub_path) else "",
        "cover_path": os.path.abspath(cover_path) if os.path.exists(cover_path) else "",
        "files_exist": {
            "epub": os.path.exists(epub_path),
            "cover": os.path.exists(cover_path)
        }
    }

    output_filename = f"d2d_payload_{book_name}_{lang}.json"
    output_path = os.path.join(NOTES_DIR, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"✅ Prepared Draft2Digital Payload for: {title}")
    print(f"  Author: {payload['author']}")
    print(f"  Publisher: {payload['publisher']}")
    print(f"  Explicit Content: {payload['explicit_content']} (General Audience)")
    print(f"  Categories: {payload['categories']}")
    print(f"  EPUB File: {payload['epub_path']} (Exists: {payload['files_exist']['epub']})")
    print(f"  Cover Image: {payload['cover_path']} (Exists: {payload['files_exist']['cover']})")
    print(f"  Saved Payload to: {output_path}\n")
    return payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare Draft2Digital Metadata Payload")
    parser.add_argument("--book", type=str, required=True, help="Book folder name (e.g. the_enchanted_april, secret_garden, gilgamesh, tono_bungay)")
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"], help="Language edition (ko or en)")
    args = parser.parse_args()
    
    prepare_payload(args.book, args.lang)
