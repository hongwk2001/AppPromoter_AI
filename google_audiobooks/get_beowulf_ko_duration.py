import os
import sys
import glob
import subprocess
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def get_duration_ffprobe(filepath):
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        return float(out.strip())
    except Exception:
        pass

    # Fallback MP3 frame header duration estimation if ffprobe not available
    try:
        import mutagen
        audio = mutagen.File(filepath)
        if audio and audio.info:
            return audio.info.length
    except Exception:
        pass

    # Simple MP3 size / bitrate estimate (e.g. 128kbps = 16000 B/s)
    size = os.path.getsize(filepath)
    # Estimate average bitrate 128kbps
    return size / 16000.0

def main():
    audio_dir = r"C:\git_repo\TKprof_book\books\beowulf\final_audio_ko"
    mp3_files = glob.glob(os.path.join(audio_dir, "*.mp3"))

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

    mp3_files.sort(key=sort_key)

    total_seconds = 0
    track_details = []

    for f in mp3_files:
        dur = get_duration_ffprobe(f)
        total_seconds += dur
        track_details.append({
            "filename": os.path.basename(f),
            "seconds": dur,
            "formatted": f"{int(dur // 60)}m {int(dur % 60):02d}s"
        })

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    # Exclude sample.mp3 from main audiobook length if sample is redundant
    main_tracks = [t for t in track_details if t["filename"] != "sample.mp3"]
    main_total_sec = sum(t["seconds"] for t in main_tracks)
    m_h = int(main_total_sec // 3600)
    m_m = int((main_total_sec % 3600) // 60)
    m_s = int(main_total_sec % 60)

    print(f"==================================================")
    print(f"🎧 BEOWULF KOREAN AUDIOBOOK DURATION SUMMARY")
    print(f"==================================================")
    print(f"• Main Audiobook Duration: {m_h} Hours {m_m} Minutes {m_s} Seconds ({m_h}:{m_m:02d}:{m_s:02d})")
    print(f"• Full Album (incl. Sample): {hours} Hours {minutes} Minutes {seconds} Seconds ({hours}:{minutes:02d}:{seconds:02d})")
    print(f"• Total Files: {len(mp3_files)} MP3 Tracks\n")

    print("📊 TRACK BREAKDOWN:")
    for t in track_details:
        print(f"  - {t['filename']:<28}: {t['formatted']}")

if __name__ == "__main__":
    main()
