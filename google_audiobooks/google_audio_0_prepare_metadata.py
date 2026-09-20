"""
google_audio_0_prepare_metadata.py
Generates a single, unified JSON metadata payload formatted specifically for
Google Play Books Partner Center Audiobook Publishing.
"""

import os
import sys
import json
import glob
import argparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")
os.makedirs(NOTES_DIR, exist_ok=True)

AUDIOBOOK_PRESETS = {
    "blue_castle": {
        "title_en": "The Blue Castle (Audiobook)",
        "title_ko": "블루 캐슬 (The Blue Castle) - 오디오북",
        "subtitle_en": "L. M. Montgomery's Beloved Classic Romance",
        "subtitle_ko": "L. M. 몽고메리가 선사하는 가슴 설레는 고전 로맨스 성장 소설",
        "author_en": "L. M. Montgomery",
        "author_ko": "L. M. 몽고메리",
        "publisher": "TKPROF LLC",
        "narrator_en": "TKPROF AI",
        "narrator_ko": "TKPROF AI",
        "categories": ["FICTION / Classics", "FICTION / Romance / General", "FICTION / Women's Fiction"],
        "price_usd": "9.99"
    },
    "beowulf": {
        "title_en": "Beowulf: Spectacular Modern English Edition (Audiobook)",
        "title_ko": "베오울프: 스펙터클 현대 한국어판 (오디오북)",
        "subtitle_en": "Modern English Edition Audiobook",
        "subtitle_ko": "현대어 한국어 오디오북",
        "author_en": "Anonymous",
        "author_ko": "작자 미상",
        "publisher": "TKPROF LLC",
        "narrator_en": "TKPROF LLC",
        "narrator_ko": "TKPROF LLC",
        "categories": ["FICTION / Classics", "FICTION / Action & Adventure"],
        "price_usd": "9.99"
    },
    "dracula": {
        "title_en": "Dracula: Bilingual English-Korean Edition (Audiobook)",
        "title_ko": "드라큘라 (Dracula) - 영한 대역판 오디오북",
        "subtitle_en": "Bram Stoker's Gothic Classic (Bilingual Parallel Edition)",
        "subtitle_ko": "문장별 영한 대역 리스닝 & 영어 학습 오디오북",
        "author_en": "Bram Stoker",
        "author_ko": "브람 스토커",
        "publisher": "TKPROF LLC",
        "narrator_en": "Aiden (English), SunHi (Korean)",
        "narrator_ko": "Aiden (English), SunHi (Korean)",
        "categories": ["FICTION / Classics", "FICTION / Horror"],
        "price_usd": "14.99"
    },
    "gilgamesh": {
        "title_en": "The Epic of Gilgamesh: Modern Edition (Audiobook)",
        "title_ko": "길가메시 서사시: 스펙터클 현대 한국어판 (The Epic of Gilgamesh)",
        "subtitle_en": "Humanity's Oldest Classic Heroic Epic",
        "subtitle_ko": "인류 최초의 위대한 고전 서사시 오디오북",
        "author_en": "Anonymous",
        "author_ko": "작자 미상",
        "publisher": "TKPROF LLC",
        "narrator_en": "TKPROF LLC",
        "narrator_ko": "TKPROF AI",
        "categories": ["FICTION / Classics", "FICTION / Action & Adventure"],
        "price_usd": "9.99"
    }
}

def resolve_book_path(book_name):
    if os.path.isabs(book_name) and os.path.exists(book_name):
        return book_name, os.path.basename(book_name)
    
    candidates = [
        os.path.join(r"C:\git_repo\TKprof_book\books", book_name),
        os.path.join(BASE_DIR, book_name)
    ]
    for c in candidates:
        if os.path.exists(c):
            return c, book_name
    return None, book_name

def prepare_audio_metadata(book_name, lang="ko"):
    book_path, b_key = resolve_book_path(book_name)
    if not book_path:
        print(f"Error: Could not locate book folder for '{book_name}'")
        return None

    preset = AUDIOBOOK_PRESETS.get(b_key, {})

    # Text fields
    if lang == "ko":
        title = preset.get("title_ko", f"{b_key} (오디오북)")
        subtitle = preset.get("subtitle_ko", "")
        author = preset.get("author_ko", "L. M. 몽고메리")
        narrator = preset.get("narrator_ko", "TKPROF AI")
    else:
        title = preset.get("title_en", f"{b_key} (Audiobook)")
        subtitle = preset.get("subtitle_en", "")
        author = preset.get("author_en", "L. M. Montgomery")
        narrator = preset.get("narrator_en", "TKPROF AI")

    # Descriptions & Custom JSON Metadata
    description = ""
    g_json_path = os.path.join(book_path, "google_play_audiobook_metadata.json")
    if os.path.exists(g_json_path):
        try:
            with open(g_json_path, "r", encoding="utf-8") as gf:
                g_data = json.load(gf)
                desc_obj = g_data.get("description", {})
                if isinstance(desc_obj, dict):
                    description = desc_obj.get("korean_blurb" if lang == "ko" else "english_blurb", "")
                elif isinstance(desc_obj, str):
                    description = desc_obj
        except Exception as e:
            print(f"Warning loading google_play_audiobook_metadata.json: {e}")

    if not description:
        desc_files = [
            os.path.join(book_path, f"overview_{lang}.txt"),
            os.path.join(book_path, f"introduction_{lang}.txt"),
            os.path.join(book_path, f"copyright_{lang}.txt"),
            os.path.join(book_path, "metadata.md")
        ]
        for path in desc_files:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    description = f.read().strip()
                    break

    # Cover Image
    cover_candidates = [
        os.path.join(book_path, "beowulf_cover_en.jpg"),
        os.path.join(book_path, f"cover_{lang}.jpg"),
        os.path.join(book_path, f"cover_{lang}.png"),
        os.path.join(book_path, "beowulfcover2400.jpg"),
        os.path.join(book_path, "cover_2400x2400.jpg"),
        os.path.join(book_path, "cover.jpg"),
        os.path.join(book_path, "cover.png")
    ]
    cover_path = ""
    for c in cover_candidates:
        if os.path.exists(c):
            cover_path = os.path.abspath(c)
            break

    # Audio Files Directory (final_audio_ko or final_audio_en or final_audio)
    audio_dir_candidates = [
        os.path.join(book_path, f"final_audio_{lang}"),
        os.path.join(book_path, "final_audio"),
        os.path.join(book_path, "audio")
    ]
    audio_dir = ""
    for ad in audio_dir_candidates:
        if os.path.exists(ad):
            audio_dir = os.path.abspath(ad)
            break

    # Inventory MP3 files
    audio_files = []
    if audio_dir:
        all_mp3s = glob.glob(os.path.join(audio_dir, "*.mp3"))
        mp3_paths = [p for p in all_mp3s if "podcast" not in os.path.basename(p).lower() and "retail_sample" not in os.path.basename(p).lower()]
        
        # Check if language suffixed files exist
        lang_suffixed = [p for p in mp3_paths if f"_{lang}.mp3" in os.path.basename(p).lower()]
        if lang_suffixed:
            mp3_paths = lang_suffixed
        def sort_key(p):
            fname = os.path.basename(p).lower()
            if fname in ["opening_credits.mp3", "opening.mp3"]:
                return (0, 0)
            elif "intro" in fname:
                return (0, 1)
            elif fname == "closing.mp3":
                return (2, 0)
            elif fname == "closing_credits.mp3":
                return (2, 1)
            elif fname == "sample.mp3":
                return (3, 0)
            else:
                nums = "".join([ch for ch in fname if ch.isdigit()])
                val = int(nums) if nums else 500
                return (1, val)

        mp3_paths.sort(key=sort_key)
        audio_files = list(dict.fromkeys(mp3_paths))

    # Calculate exact duration (excluding sample.mp3)
    main_tracks = [f for f in audio_files if "sample.mp3" not in os.path.basename(f).lower()]
    total_sec = 0.0
    for fpath in main_tracks:
        try:
            import subprocess
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", fpath]
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            total_sec += float(out.strip())
        except Exception:
            total_sec += os.path.getsize(fpath) / 16000.0

    dur_h = int(total_sec // 3600)
    dur_m = int((total_sec % 3600) // 60)
    dur_s = int(total_sec % 60)
    duration_formatted = f"{dur_h:02d}:{dur_m:02d}:{dur_s:02d}"

    metadata = {
        "book_id": b_key,
        "format": "AUDIOBOOK",
        "language_code": lang,
        "language_name": "Korean" if lang == "ko" else "English",
        "book_info": {
            "title": title,
            "subtitle": subtitle,
            "author": author,
            "narrator": narrator,
            "publisher": preset.get("publisher", "TKPROF LLC"),
            "duration": duration_formatted,
            "duration_seconds": round(total_sec, 2),
            "categories": preset.get("categories", ["FICTION / Classics"]),
            "description": description
        },
        "contributors": [
            {
                "name": author,
                "role": "Author",
                "bio": (
                    "《베오울프》(Beowulf)는 8세기~11세기경 고대 영어로 작성된 영문학 최선두의 고대 서사시로, 작자는 미상이나 인류 문학사에서 영웅 서사시의 원형으로 평가받습니다."
                    if "beowulf" in b_key else ""
                )
            },
            {
                "name": narrator,
                "role": "Narrator",
                "bio": (
                    "TKPROF LLC는 고전 문학의 현대화 및 오디오북 퍼블리싱 전문 팀입니다. 본 오디오북 개정판은 고대 영문학 대서사시 《베오울프》 원작을 현대 한국어 독자와 오디오북 청취 환경에 맞춰 정교하게 편역 및 낭독 제작했습니다: 1) 번역 방식: 딱딱하고 장황한 고어 직역을 벗어나 현대 웹소설의 스펙터클한 문법과 속도감 넘치는 현대 구어체로 완판 재번역했습니다. 2) 낭독 및 음성 연출: 성우 및 AI 내레이션 기술을 조합하여 장면별 서사적 긴장감, 전투 몰입감, 문장 호흡을 오디오 청취에 최적화하여 연출했습니다. 3) 생략 없는 완판 서사 구조를 보존하여 오디오북 청취자에게 최고의 몰입감을 제공합니다."
                    if "beowulf" in b_key else ""
                )
            }
        ],
        "content_files": {
            "cover_image_path": cover_path,
            "cover_exists": bool(cover_path),
            "audio_dir": audio_dir,
            "audio_track_count": len(audio_files),
            "audio_files": audio_files
        },
        "pricing": {
            "digital_price_usd": preset.get("price_usd", "9.99"),
            "currency": "USD"
        }
    }

    out_file = os.path.join(NOTES_DIR, f"google_audio_metadata_{b_key}_{lang}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Prepared Google Books Audiobook Metadata File: {out_file}")
    print(f"  Title: {title}")
    print(f"  Author: {author}")
    print(f"  Cover Exists: {metadata['content_files']['cover_exists']}")
    print(f"  Audio Track Count: {metadata['content_files']['audio_track_count']} MP3s\n")
    return metadata

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare Google Play Books Audiobook Metadata")
    parser.add_argument("--book", type=str, required=True, help="Book key or folder path")
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    args = parser.parse_args()

    prepare_audio_metadata(args.book, args.lang)
