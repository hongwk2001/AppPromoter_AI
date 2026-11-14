"""
gumroad_0_prepare_metadata.py
Builds a Gumroad product payload for one ebook from the existing unified
metadata (notes/d2d_metadata_<book>_<lang>.json), so the listing text is
reused instead of rewritten.

Output: notes/gumroad_<book>_<lang>.json

Usage:
  python gumroad/gumroad_0_prepare_metadata.py --book secret_garden --lang ko
  python gumroad/gumroad_0_prepare_metadata.py --book secret_garden --lang ko --free

Defaults to the same price the book has on other stores, so a Gumroad copy
never undercuts KDP or Google. --free makes it $0+ (pay what you want);
only use that for titles you are not selling on Amazon.
"""

import os
import sys
import json
import argparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES_DIR = os.path.join(ROOT, "notes")

# Shown at the end of every description. Gumroad copies carry no ISBN:
# a D2D-assigned ISBN belongs to D2D's distribution only.
ATTRIBUTION = {
    "ko": (
        "\n\n---\n"
        "번역·편집: TKPROF LLC\n"
        "원작: {author} (퍼블릭 도메인)\n"
        "본 한국어판의 번역문과 편집은 TKPROF LLC의 저작물입니다.\n"
        "파일 형식: EPUB (DRM 없음)"
    ),
    "en": (
        "\n\n---\n"
        "Edition prepared by TKPROF LLC\n"
        "Original work: {author} (public domain)\n"
        "The text of this edition, including any translation and editing, is by TKPROF LLC.\n"
        "Format: EPUB (DRM-free)"
    ),
}

GUMROAD_TAG_LIMIT = 5


def build_payload(book, lang, free):
    src = os.path.join(NOTES_DIR, f"d2d_metadata_{book}_{lang}.json")
    if not os.path.exists(src):
        sys.exit(f"Error: no metadata at {src}")
    with open(src, encoding="utf-8") as f:
        d = json.load(f)

    s1, s2, s3 = d["step1_metadata"], d["step2_details"], d["step3_pricing"]
    author = s1.get("author", "")
    store_price = s3.get("digital_price_usd", "3.99")

    description = s2.get("full_description_text", "").strip()
    description += ATTRIBUTION.get(lang, ATTRIBUTION["en"]).format(author=author)

    title = s1["title"]
    files = [p for p in [s2.get("epub_path")] if p]

    payload = {
        "book_id": book,
        "language_code": lang,
        "product_type": "Ebook",
        "name": title,
        "url_slug": f"{book.replace('_', '-')}-{lang}",
        "summary": s2.get("short_description", "")[:300],
        "description": description,
        "pricing": {
            "pay_what_you_want": True if free else False,
            "price_usd": "0" if free else store_price,
            "suggested_price_usd": store_price if free else None,
            "matches_other_stores": not free,
        },
        "tags": s1.get("search_terms", [])[:GUMROAD_TAG_LIMIT],
        "cover_image_path": s1.get("cover_image_path"),
        "files": files,
        "isbn": None,
        "notes": [
            "Gumroad's cover area is wide (about 1280x720) and the thumbnail is square (600x600); "
            "a portrait book cover works but may be letterboxed.",
            "Leave the product unpublished for the test; publish only after checking the preview.",
        ],
    }

    missing = [p for p in files + [payload["cover_image_path"]] if p and not os.path.exists(p)]
    return payload, missing


def main():
    ap = argparse.ArgumentParser(description="Prepare a Gumroad ebook payload from existing metadata")
    ap.add_argument("--book", required=True, help="Book id, e.g. secret_garden")
    ap.add_argument("--lang", default="ko", help="Language code (ko or en)")
    ap.add_argument("--free", action="store_true", help="List as $0+ pay-what-you-want")
    args = ap.parse_args()

    payload, missing = build_payload(args.book, args.lang, args.free)
    out = os.path.join(NOTES_DIR, f"gumroad_{args.book}_{args.lang}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    p = payload["pricing"]
    price = "$0+ (suggested $%s)" % p["suggested_price_usd"] if p["pay_what_you_want"] else "$" + p["price_usd"]
    print(f"Wrote {out}")
    print(f"  Name : {payload['name']}")
    print(f"  Price: {price}")
    print(f"  Tags : {', '.join(payload['tags'])}")
    print(f"  Files: {', '.join(payload['files']) or '(none)'}")
    if missing:
        print("  Not found on this machine (fine if you run this on another computer):")
        for m in missing:
            print(f"    - {m}")


if __name__ == "__main__":
    main()
