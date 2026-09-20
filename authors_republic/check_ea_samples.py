import os
import sys
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BOOK_DIR = r"C:\git_repo\TKprof_book\books\the_enchanted_april"
KO_SAMPLE = os.path.join(BOOK_DIR, "final_audio_ko", "sample.mp3")
EN_SAMPLE = os.path.join(BOOK_DIR, "final_audio", "sample.mp3")

def probe_file(filepath):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return None
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    dur = float(res.stdout.strip())
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"File: {filepath}")
    print(f"  Duration: {dur:.2f} s ({dur/60.0:.2f} mins)")
    print(f"  Size:     {size_mb:.2f} MB")
    return dur

if __name__ == "__main__":
    print("Checking Korean sample:")
    ko_dur = probe_file(KO_SAMPLE)

    print("\nChecking English sample:")
    en_dur = probe_file(EN_SAMPLE)
