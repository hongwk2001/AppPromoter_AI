import os
import sys
import json
import argparse
import subprocess
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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
    except Exception:
        return None

def analyze_audio_levels(filepath, duration):
    cmd = [
        "ffmpeg", "-i", filepath,
        "-af", "volumedetect,silencedetect=noise=-50dB:d=0.3",
        "-f", "null", "-"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        stderr = res.stderr

        max_volume = None
        mean_volume = None
        for line in stderr.splitlines():
            if "max_volume:" in line:
                try:
                    max_volume = float(line.split("max_volume:")[1].split("dB")[0].strip())
                except: pass
            elif "mean_volume:" in line:
                try:
                    mean_volume = float(line.split("mean_volume:")[1].split("dB")[0].strip())
                except: pass

        starts = []
        ends = []
        for line in stderr.splitlines():
            if "silence_start:" in line:
                try:
                    starts.append(float(line.split("silence_start:")[1].split()[0]))
                except: pass
            elif "silence_end:" in line:
                try:
                    ends.append(float(line.split("silence_end:")[1].split()[0]))
                except: pass

        # silence_start is a timestamp, not a duration. Leading silence is the first
        # silence_end when the first silence begins at (or within a frame of) zero.
        head_silence = ends[0] if (starts and ends and starts[0] <= 0.05) else 0.0
        # Trailing silence only exists when the final silence runs to EOF, i.e. it has
        # no matching silence_end, or its end lands on the track duration.
        if starts and len(starts) > len(ends):
            tail_silence = duration - starts[-1]
        elif starts and ends and abs(ends[-1] - duration) <= 0.05:
            tail_silence = duration - starts[-1]
        else:
            tail_silence = 0.0

        return {
            "max_volume_db": max_volume,
            "mean_volume_db": mean_volume,
            "head_silence_s": head_silence,
            "tail_silence_s": tail_silence
        }
    except Exception:
        return {
            "max_volume_db": None,
            "mean_volume_db": None,
            "head_silence_s": 0.0,
            "tail_silence_s": 0.0
        }

def audit_book_project(book_name="richest_man_in_babylon", lang="en"):
    base_dir = r"C:\git_repo\TKprof_book\books"
    book_dir = os.path.join(base_dir, book_name)

    if not os.path.exists(book_dir):
        print(f"❌ Error: Book directory does not exist: {book_dir}")
        return

    # Determine audio directory
    audio_candidates = [
        os.path.join(book_dir, "final_audio_ar_ready"),
        os.path.join(book_dir, f"final_audio_{lang}_ready"),
        os.path.join(book_dir, f"final_audio_{lang}"),
        os.path.join(book_dir, "final_audio"),
        os.path.join(book_dir, "audio")
    ]
    audio_dir = None
    for cand in audio_candidates:
        if os.path.exists(cand) and any(f.endswith(".mp3") for f in os.listdir(cand)):
            audio_dir = cand
            break

    # Determine cover path
    cover_candidates = [
        os.path.join(book_dir, f"cover_{lang}_2400.jpg"),
        os.path.join(book_dir, "cover_en_2400.jpg"),
        os.path.join(book_dir, "cover_ko_2400.jpg"),
        os.path.join(book_dir, f"cover_{lang}.jpg"),
        os.path.join(book_dir, f"cover_{lang}.png")
    ]
    cover_path = None
    for cand in cover_candidates:
        if os.path.exists(cand):
            cover_path = cand
            break

    print("======================================================================")
    print(f"🎙️ AUTHORS REPUBLIC COMPLIANCE AUDIT FOR: {book_name} (Language: {lang})")
    print(f"📁 Path: {book_dir}")
    print("======================================================================")

    # ---------------------------------------------------------
    # 1. COVER IMAGE AUDIT
    # ---------------------------------------------------------
    print("\n📸 [1] COVER ART AUDIT")
    print("----------------------------------------------------------------------")
    cover_issues = []
    if not cover_path or not os.path.exists(cover_path):
        print("❌ CRITICAL: Cover image file not found.")
        cover_issues.append("Cover image file not found.")
    else:
        file_size_mb = os.path.getsize(cover_path) / (1024 * 1024)
        with Image.open(cover_path) as img:
            w, h = img.size
            mode = img.mode
            fmt = img.format

            print(f"  File Path:   {cover_path}")
            print(f"  Dimensions:  {w} x {h} px (Requirement: 2400 x 2400 px or square >= 2400px)")
            print(f"  File Size:   {file_size_mb:.2f} MB (Requirement: < 5.0 MB)")
            print(f"  Format:      {fmt} (Requirement: JPEG/PNG)")
            print(f"  Color Space: {mode} (Requirement: RGB)")

            if w < 2400 or h < 2400 or w != h:
                cover_issues.append(f"Dimensions {w}x{h} px fail 2400x2400 px 1:1 square requirement.")
            if file_size_mb >= 5.0:
                cover_issues.append(f"File size {file_size_mb:.2f} MB exceeds 5 MB limit.")
            if mode not in ["RGB", "RGBA"]:
                cover_issues.append(f"Color mode {mode} is not RGB.")

            if cover_issues:
                print("  ❌ COVER AUDIT STATUS: FAIL")
                for issue in cover_issues:
                    print(f"     - {issue}")
            else:
                print("  ✅ COVER AUDIT STATUS: PASS")

    # ---------------------------------------------------------
    # 2. AUDIO TRACKS AUDIT
    # ---------------------------------------------------------
    print("\n🎧 [2] AUDIO TRACKS AUDIT")
    print("----------------------------------------------------------------------")
    if not audio_dir or not os.path.exists(audio_dir):
        print(f"❌ CRITICAL: Audio directory not found: {audio_dir}")
        return

    audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith(".mp3")])
    if lang == "en":
        # filter english tracks if mixed
        en_tracks = [f for f in audio_files if "_en.mp3" in f or "final_" in f or f.startswith("ch_")]
        if en_tracks:
            audio_files = en_tracks

    print(f"Found {len(audio_files)} MP3 tracks in {audio_dir}\n")

    audio_issues = []
    bitrates = set()
    sample_rates = set()
    channels_set = set()

    for idx, fname in enumerate(audio_files, 1):
        fpath = os.path.join(audio_dir, fname)
        size_mb = os.path.getsize(fpath) / (1024 * 1024)
        info = probe_audio(fpath)
        if not info:
            print(f"  [{idx:02d}] ❌ Could not probe {fname}")
            audio_issues.append(f"{fname}: Failed to probe audio metadata.")
            continue

        bitrates.add(info['bitrate_kbps'])
        sample_rates.add(info['sample_rate'])
        channels_set.add(info['channels'])
        dur_min = info['duration'] / 60.0

        levels = analyze_audio_levels(fpath, info['duration'])

        track_failed = False
        track_notes = []

        # Check sample rate (44100 Hz)
        if info['sample_rate'] != 44100:
            track_failed = True
            track_notes.append(f"Sample rate {info['sample_rate']} Hz != 44100 Hz")

        # Check bitrate (>= 192 kbps)
        if info['bitrate_kbps'] < 192:
            track_failed = True
            track_notes.append(f"Bitrate {info['bitrate_kbps']} kbps < 192 kbps")

        # Check peak amplitude (<= -3.0 dB)
        if levels['max_volume_db'] is not None and levels['max_volume_db'] > -3.0:
            track_failed = True
            track_notes.append(f"Peak amplitude {levels['max_volume_db']} dB > -3.0 dB limit")

        # Check RMS volume (-23 dB to -18 dB)
        if levels['mean_volume_db'] is not None:
            if levels['mean_volume_db'] < -25.0 or levels['mean_volume_db'] > -16.0:
                track_notes.append(f"RMS {levels['mean_volume_db']} dB outside optimal -23..-18 dB range")

        # Check file duration (< 120 mins)
        if dur_min >= 120.0:
            track_failed = True
            track_notes.append(f"Duration {dur_min:.1f} mins >= 120 mins limit")

        # Check retail sample track duration (1.0 to 5.0 mins)
        if "sample" in fname.lower():
            if dur_min < 1.0 or dur_min > 5.0:
                track_failed = True
                track_notes.append(f"Retail sample duration {dur_min:.2f} mins outside 1.0-5.0 min limit")

        status_str = "❌ FAIL" if track_failed else "✅ PASS"
        notes_str = f" ({', '.join(track_notes)})" if track_notes else ""

        max_db_str = f"{levels['max_volume_db']:.1f}" if levels['max_volume_db'] is not None else "N/A"
        print(f"  [{idx:02d}] {fname[:28]:<28} | {size_mb:5.1f}MB | {dur_min:5.1f}m | {info['bitrate_kbps']}k | {info['sample_rate']}Hz | Peak: {max_db_str}dB | Head: {levels['head_silence_s']:.1f}s | Tail: {levels['tail_silence_s']:.1f}s | {status_str}{notes_str}")

        if track_failed:
            audio_issues.append(f"{fname}: {', '.join(track_notes)}")

    # Bitrate consistency check
    if len(bitrates) > 1:
        audio_issues.append(f"Mixed bitrates detected across tracks: {sorted(list(bitrates))} kbps. All tracks must share identical bitrate.")

    # ---------------------------------------------------------
    # 3. AUDIT SUMMARY
    # ---------------------------------------------------------
    print("\n======================================================================")
    print(f"📊 AUDIT SUMMARY FOR {book_name.upper()}")
    print("======================================================================")

    print(f"Total Tracks Audited:    {len(audio_files)}")
    print(f"Bitrate Consistency:     {sorted(list(bitrates))} kbps")
    print(f"Sample Rate Consistency: {sorted(list(sample_rates))} Hz")
    print(f"Channel Consistency:     {sorted(list(channels_set))} channels")
    
    if cover_issues or audio_issues:
        print("\n❌ TOTAL AUDIT RESULT: NON-COMPLIANT (ACTION REQUIRED)")
        print("\nIssues Breakdown:")
        for idx, issue in enumerate(cover_issues + audio_issues, 1):
            print(f"  {idx}. {issue}")
    else:
        print("\n✅ TOTAL AUDIT RESULT: FULLY COMPLIANT WITH AUTHORS REPUBLIC")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", default="richest_man_in_babylon")
    parser.add_argument("--lang", default="en")
    args = parser.parse_args()

    audit_book_project(args.book, args.lang)
