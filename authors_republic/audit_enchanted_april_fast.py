import os
import sys
import json
import subprocess
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BOOK_DIR = r"C:\git_repo\TKprof_book\books\the_enchanted_april"
AUDIO_DIR = os.path.join(BOOK_DIR, "final_audio_ko")

def probe_audio(filepath):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate,channels,bit_rate,codec_name",
        "-show_entries", "format=duration,bit_rate",
        "-of", "json",
        filepath
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        stream = data.get("streams", [{}])[0]
        fmt = data.get("format", {})
        
        sample_rate = int(stream.get("sample_rate", 0))
        channels = int(stream.get("channels", 0))
        duration = float(fmt.get("duration", 0.0))
        bitrate_str = stream.get("bit_rate") or fmt.get("bit_rate")
        bitrate = int(bitrate_str) // 1000 if bitrate_str else 0
        
        return {
            "sample_rate": sample_rate,
            "channels": channels,
            "duration": duration,
            "bitrate_kbps": bitrate,
            "codec": stream.get("codec_name", "unknown")
        }
    except Exception as e:
        return None

def fast_audit():
    print("======================================================================")
    print(f"🎙️ AUTHORS REPUBLIC COMPLIANCE AUDIT FOR: {BOOK_DIR}")
    print("======================================================================")

    # 1. Cover Image Audit
    print("\n📸 [1] COVER ART AUDIT")
    cover_jpg = os.path.join(BOOK_DIR, "cover_ko.jpg")
    cover_png = os.path.join(BOOK_DIR, "cover_ko.png")
    target_cover = cover_jpg if os.path.exists(cover_jpg) else cover_png

    cover_issues = []
    if not os.path.exists(target_cover):
        cover_issues.append("Cover image file not found.")
        print("❌ CRITICAL: Cover image file not found.")
    else:
        file_size_mb = os.path.getsize(target_cover) / (1024 * 1024)
        with Image.open(target_cover) as img:
            w, h = img.size
            mode = img.mode
            fmt = img.format
            print(f"  Path:       {target_cover}")
            print(f"  Dimensions: {w} x {h} px (Req: 2400 x 2400 px)")
            print(f"  Size:       {file_size_mb:.2f} MB (Req: < 5.0 MB)")
            print(f"  Format:     {fmt} (Req: JPEG/PNG)")
            print(f"  Color Mode: {mode} (Req: RGB)")

            if w != 2400 or h != 2400:
                cover_issues.append(f"Dimensions {w}x{h} px != 2400x2400 px square.")
            if file_size_mb >= 5.0:
                cover_issues.append(f"File size {file_size_mb:.2f} MB >= 5.0 MB.")
            if mode not in ["RGB", "RGBA"]:
                cover_issues.append(f"Color mode {mode} != RGB.")

            if cover_issues:
                print("  ❌ COVER AUDIT: FAIL")
            else:
                print("  ✅ COVER AUDIT: PASS")

    # 2. Audio Audit
    print("\n🎧 [2] AUDIO TRACKS AUDIT")
    audio_files = sorted([f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")])
    print(f"Found {len(audio_files)} MP3 tracks\n")

    audio_issues = []
    bitrates = set()
    sample_rates = set()
    channels_set = set()

    for idx, fname in enumerate(audio_files, 1):
        fpath = os.path.join(AUDIO_DIR, fname)
        size_mb = os.path.getsize(fpath) / (1024 * 1024)
        info = probe_audio(fpath)
        if not info:
            audio_issues.append(f"{fname}: Failed to probe metadata.")
            continue

        bitrates.add(info['bitrate_kbps'])
        sample_rates.add(info['sample_rate'])
        channels_set.add(info['channels'])
        dur_min = info['duration'] / 60.0

        track_failed = False
        track_notes = []

        if info['sample_rate'] != 44100:
            track_failed = True
            track_notes.append(f"Sample rate {info['sample_rate']} Hz != 44100 Hz")

        if info['bitrate_kbps'] < 192:
            track_failed = True
            track_notes.append(f"Bitrate {info['bitrate_kbps']} kbps < 192 kbps")

        if dur_min >= 120.0:
            track_failed = True
            track_notes.append(f"Duration {dur_min:.1f}m >= 120m limit")

        if fname == "sample.mp3":
            if dur_min < 1.0 or dur_min > 5.0:
                track_failed = True
                track_notes.append(f"Retail sample duration {dur_min:.2f}m outside 1-5m limit")

        status = "❌ FAIL" if track_failed else "✅ PASS"
        notes = f" ({', '.join(track_notes)})" if track_notes else ""
        print(f"  [{idx:02d}] {fname:<28} | {size_mb:5.1f}MB | {dur_min:5.1f}m | {info['bitrate_kbps']}k | {info['sample_rate']}Hz | {status}{notes}")

        if track_failed:
            audio_issues.append(f"{fname}: {', '.join(track_notes)}")

    if len(bitrates) > 1:
        audio_issues.append(f"Mixed bitrates: {sorted(list(bitrates))} kbps.")

    print("\n======================================================================")
    print("📊 AUDIT RESULTS SUMMARY")
    print("======================================================================")
    all_issues = cover_issues + audio_issues
    if all_issues:
        print(f"❌ TOTAL AUDIT RESULT: NON-COMPLIANT ({len(all_issues)} ISSUES DETECTED)")
        for idx, iss in enumerate(all_issues, 1):
            print(f"  {idx}. {iss}")
    else:
        print("✅ TOTAL AUDIT RESULT: FULLY COMPLIANT")

if __name__ == "__main__":
    fast_audit()
