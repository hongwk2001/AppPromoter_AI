"""
split_rmib_tracks.py
Splits oversized tracks in final_audio_ar_ready for The Richest Man in Babylon
into a new final_audio_ar_split directory, then regenerates the AR payload.
AR limit: 45MB per file.
"""

import os
import sys
import json
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BOOK_DIR = r"C:\git_repo\TKprof_book\books\richest_man_in_babylon"
IN_DIR = os.path.join(BOOK_DIR, "final_audio_ar_ready")
OUT_DIR = os.path.join(BOOK_DIR, "final_audio_ar_split")
NOTES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notes")
PAYLOAD_OUT = os.path.join(NOTES_DIR, "ar_payload_richest_man_in_babylon_en.json")

MAX_MB = 40.0  # safe margin below 45MB limit

os.makedirs(OUT_DIR, exist_ok=True)


def get_duration(filepath):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        filepath
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def split_and_copy():
    all_files = sorted([f for f in os.listdir(IN_DIR) if f.endswith(".mp3")])
    ready_files = []

    print(f"Processing {len(all_files)} files from {IN_DIR} (max {MAX_MB} MB each)...\n")

    for filename in all_files:
        src = os.path.join(IN_DIR, filename)
        size_mb = os.path.getsize(src) / (1024 * 1024)

        if size_mb <= MAX_MB:
            dst = os.path.join(OUT_DIR, filename)
            if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
                with open(src, "rb") as rf, open(dst, "wb") as wf:
                    wf.write(rf.read())
                print(f"  Copied   {filename} ({size_mb:.1f} MB)")
            else:
                print(f"  Skipped  {filename} ({size_mb:.1f} MB) -- already in output")
            ready_files.append(dst)
        else:
            duration = get_duration(src)
            num_parts = int(size_mb // MAX_MB) + 1
            part_duration = duration / float(num_parts)

            print(f"  Splitting {filename} ({size_mb:.1f} MB, {duration:.1f}s) -> {num_parts} parts")

            for p_idx in range(num_parts):
                part_name = filename.replace(".mp3", f"_part{p_idx + 1}.mp3")
                part_path = os.path.join(OUT_DIR, part_name)

                start_time = p_idx * part_duration

                if not os.path.exists(part_path):
                    if p_idx == num_parts - 1:
                        cmd = ["ffmpeg", "-y", "-ss", str(start_time), "-i", src, "-c", "copy", part_path]
                    else:
                        cmd = ["ffmpeg", "-y", "-ss", str(start_time), "-i", src,
                               "-t", str(part_duration), "-c", "copy", part_path]
                    subprocess.run(cmd, capture_output=True, check=True)
                    part_mb = os.path.getsize(part_path) / (1024 * 1024)
                    print(f"       -> {part_name} ({part_mb:.1f} MB)")
                else:
                    part_mb = os.path.getsize(part_path) / (1024 * 1024)
                    print(f"       -> {part_name} ({part_mb:.1f} MB) -- already exists")

                ready_files.append(part_path)

    # Return in proper playback order: intro → chapters (sorted) → copyright
    intro_files   = [f for f in ready_files if "final_intro" in os.path.basename(f)]
    chapter_files = sorted([f for f in ready_files if os.path.basename(f).startswith("final_ch_")])
    closing_files = [f for f in ready_files if "final_copyright" in os.path.basename(f)]
    ordered = intro_files + chapter_files + closing_files

    print(f"\nTotal tracks ready: {len(ordered)} in {OUT_DIR}")
    return ordered


def update_payload(audio_files):
    cover_path = os.path.join(BOOK_DIR, "cover_en_2400.jpg")
    intro_path = os.path.join(BOOK_DIR, "introduction_en.txt")

    if os.path.exists(intro_path):
        with open(intro_path, "r", encoding="utf-8") as f:
            description_text = f.read()
    else:
        with open(PAYLOAD_OUT, "r", encoding="utf-8") as f:
            existing = json.load(f)
        description_text = existing.get("description", "")

    opening = next((f for f in audio_files if "final_intro" in os.path.basename(f)), "")
    closing = next((f for f in audio_files if "final_copyright" in os.path.basename(f)), "")
    sample = next((f for f in audio_files if "final_ch_00" in os.path.basename(f)
                   and "part" not in os.path.basename(f)), audio_files[1] if len(audio_files) > 1 else "")

    payload = {
        "book_id": "richest_man_in_babylon",
        "language_code": "en",
        "language_name": "English",
        "title": "The Richest Man in Babylon: Modern English Edition",
        "subtitle": "The Success Secrets of the Ancients - Personal Finance Classic",
        "author_first": "George S.",
        "author_last": "Clason",
        "narrator_first": "TKPROF",
        "narrator_last": "LLC",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": False,
        "series_name": "",
        "series_number": "",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "BUSINESS & ECONOMICS / Personal Finance / General",
            "FICTION / Classics"
        ],
        "keywords": "Richest Man in Babylon; personal finance; George Clason; money; investing; audiobook; wealth",
        "price_usd": "9.99",
        "cover_path": cover_path,
        "audio_dir": OUT_DIR,
        "opening_track": opening,
        "closing_track": closing,
        "sample_track": sample,
        "audio_tracks": audio_files
    }

    with open(PAYLOAD_OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\nPayload updated -> {PAYLOAD_OUT}")
    print(f"   Tracks:  {len(audio_files)}")
    print(f"   Opening: {os.path.basename(opening)}")
    print(f"   Closing: {os.path.basename(closing)}")
    print(f"   Sample:  {os.path.basename(sample)}")
    return payload


if __name__ == "__main__":
    audio_files = split_and_copy()
    update_payload(audio_files)
    print("\nPrep complete! Ready to run automate_ar_publish.py")
