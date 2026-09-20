"""
normalize_rmib_tracks.py
Post-processes final_audio_ar_split tracks for Authors Republic compliance:
  1. Normalize RMS to -20 dB (target center of the -23 to -18 dB window)
  2. Add 2 seconds of silence at the beginning and end of each track
Output: final_audio_ar_normalized/
"""

import os
import sys
import json
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BOOK_DIR    = r"C:\git_repo\TKprof_book\books\richest_man_in_babylon"
IN_DIR      = os.path.join(BOOK_DIR, "final_audio_ar_split")
OUT_DIR     = os.path.join(BOOK_DIR, "final_audio_ar_normalized")
NOTES_DIR   = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notes")
PAYLOAD_IN  = os.path.join(NOTES_DIR, "ar_payload_richest_man_in_babylon_en.json")
PAYLOAD_OUT = PAYLOAD_IN  # overwrite in-place

SILENCE_SEC = 2.0   # seconds of silence to pad at start and end
TARGET_LUFS = -20.0 # center of -23 to -18 dB RMS window

os.makedirs(OUT_DIR, exist_ok=True)


def get_rms_lufs(filepath):
    """Run ffmpeg loudnorm in analysis mode, return integrated loudness."""
    cmd = [
        "ffmpeg", "-i", filepath,
        "-af", "loudnorm=I=-20:TP=-1.5:LRA=11:print_format=json",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    # loudnorm JSON is in stderr
    stderr = res.stderr
    try:
        start = stderr.rfind("{")
        end   = stderr.rfind("}") + 1
        data  = json.loads(stderr[start:end])
        return float(data.get("input_i", 0))
    except Exception:
        return None


def normalize_and_pad(src, dst):
    """
    Two-pass loudnorm + silence padding via ffmpeg filter_complex.
    silence at start: aevalsrc=0:d=2
    silence at end:   aevalsrc=0:d=2
    concat all three.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", src,
        "-filter_complex",
        (
            f"[0:a]loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11[normed];"
            f"aevalsrc=0:d={SILENCE_SEC}[sil_start];"
            f"aevalsrc=0:d={SILENCE_SEC}[sil_end];"
            f"[sil_start][normed][sil_end]concat=n=3:v=0:a=1[out]"
        ),
        "-map", "[out]",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "192k",
        dst
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[-500:]}")
        return False
    return True


def process_all():
    with open(PAYLOAD_IN, "r", encoding="utf-8") as f:
        payload = json.load(f)

    track_paths = payload["audio_tracks"]
    new_tracks  = []

    print(f"Processing {len(track_paths)} tracks...\n")

    for src in track_paths:
        filename = os.path.basename(src)
        dst = os.path.join(OUT_DIR, filename)

        if os.path.exists(dst):
            size_mb = os.path.getsize(dst) / (1024*1024)
            print(f"  SKIP  {filename} ({size_mb:.1f} MB) -- already normalized")
            new_tracks.append(dst)
            continue

        src_size_mb = os.path.getsize(src) / (1024*1024) if os.path.exists(src) else 0
        print(f"  NORM  {filename} ({src_size_mb:.1f} MB) ...", end=" ", flush=True)

        ok = normalize_and_pad(src, dst)
        if ok:
            dst_size_mb = os.path.getsize(dst) / (1024*1024)
            print(f"-> {dst_size_mb:.1f} MB  OK")
            new_tracks.append(dst)
        else:
            print("FAILED")

    # Update payload paths
    def remap(old_path):
        if not old_path:
            return old_path
        return os.path.join(OUT_DIR, os.path.basename(old_path))

    payload["audio_dir"]      = OUT_DIR
    payload["opening_track"]  = remap(payload["opening_track"])
    payload["closing_track"]  = remap(payload["closing_track"])
    payload["sample_track"]   = remap(payload["sample_track"])
    payload["audio_tracks"]   = new_tracks

    with open(PAYLOAD_OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\nPayload updated -> {PAYLOAD_OUT}")
    print(f"   Tracks:  {len(new_tracks)}")
    print(f"   Dir:     {OUT_DIR}")
    print("\nDone! Ready to run automate_ar_publish.py")


if __name__ == "__main__":
    process_all()
