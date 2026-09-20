"""
generate_feedback_audio_tracks.py
Synthesizes concise closing tracks and separate appendix tracks for:
  1. Korean Edition (books/the_enchanted_april/final_audio_ko/)
  2. English Edition (books/the_enchanted_april/final_audio/)
Matches Authors Republic specifications (CBR 256kbps, 44.1kHz, 1.0s-2.0s silence padding).
"""

import os
import sys
import asyncio
import subprocess
import edge_tts

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BOOK_DIR = r"C:\git_repo\TKprof_book\books\the_enchanted_april"
KO_AUDIO_DIR = os.path.join(BOOK_DIR, "final_audio_ko")
EN_AUDIO_DIR = os.path.join(BOOK_DIR, "final_audio")

KO_VOICE = "ko-KR-SunHiNeural"
EN_VOICE = "en-US-GuyNeural"

async def synthesize_text_to_mp3(text, voice, out_mp3_path):
    temp_raw = out_mp3_path.replace(".mp3", "_temp.mp3")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(temp_raw)

    # Process with ffmpeg: 44.1kHz, CBR 256k, 1s leading & 2s trailing silence padding
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "1.0",
        "-i", temp_raw,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "2.0",
        "-filter_complex", "[0:a][1:a][2:a]concat=n=3:v=0:a=1[aout]",
        "-map", "[aout]",
        "-ar", "44100",
        "-b:a", "256k",
        out_mp3_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    if os.path.exists(temp_raw):
        os.remove(temp_raw)
    
    size_mb = os.path.getsize(out_mp3_path) / (1024 * 1024)
    print(f"  ✅ Created: {out_mp3_path} ({size_mb:.2f} MB)")

async def main():
    print("🎙️ Synthesizing Authors Republic Compliant Closing & Appendix Tracks...")

    # 1. Korean Closing & Appendix
    print("\n--- [KOREAN EDITION] ---")
    ko_closing_text = "이것으로 마법에 걸린 4월 오디오북을 마칩니다. 저자: 엘리자베스 폰 아르님. 낭독: TKPROF AI. 들어주셔서 감사합니다."
    ko_closing_path = os.path.join(KO_AUDIO_DIR, "closing.mp3")
    await synthesize_text_to_mp3(ko_closing_text, KO_VOICE, ko_closing_path)

    ko_copyright_path = os.path.join(BOOK_DIR, "copyright_ko.txt")
    if os.path.exists(ko_copyright_path):
        with open(ko_copyright_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        appendix_text = "".join(lines[2:]).strip()
        if appendix_text:
            ko_appendix_path = os.path.join(KO_AUDIO_DIR, "final_track_24_appendix.mp3")
            await synthesize_text_to_mp3(appendix_text, KO_VOICE, ko_appendix_path)

    # 2. English Closing & Appendix
    print("\n--- [ENGLISH EDITION] ---")
    en_closing_text = "This has been The Enchanted April. Written by Elizabeth von Arnim, narrated by Ryan. The End."
    en_closing_path = os.path.join(EN_AUDIO_DIR, "closing.mp3")
    await synthesize_text_to_mp3(en_closing_text, EN_VOICE, en_closing_path)

    en_copyright_path = os.path.join(BOOK_DIR, "copyright_en.txt")
    if os.path.exists(en_copyright_path):
        with open(en_copyright_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        appendix_text_en = "".join(lines[2:]).strip()
        if appendix_text_en:
            en_appendix_path = os.path.join(EN_AUDIO_DIR, "final_track_24_appendix.mp3")
            await synthesize_text_to_mp3(appendix_text_en, EN_VOICE, en_appendix_path)

    print("\n🎉 Audio Synthesis Complete!")

if __name__ == "__main__":
    asyncio.run(main())
