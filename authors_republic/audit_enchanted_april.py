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

def analyze_audio_levels(filepath, duration):
    cmd = [
        "ffmpeg", "-i", filepath,
        "-af", "volumedetect,silencedetect=noise=-50dB:d=0.3",
        "-f", "null", "-"
    ]
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

    # Silence detection
    silences = []
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

    head_silence = starts[0] if starts else 0.0
    tail_silence = 0.0
    if ends and starts and len(ends) >= len(starts):
        tail_silence = duration - starts[-1]

    return {
        "max_volume_db": max_volume,
        "mean_volume_db": mean_volume,
        "head_silence_s": head_silence,
        "tail_silence_s": tail_silence
    }

def run_full_audit():
    print("======================================================================")
    print(f"🎙️ AUTHORS REPUBLIC COMPLIANCE AUDIT FOR: {BOOK_DIR}")
    print("======================================================================")

    # ---------------------------------------------------------
    # 1. COVER IMAGE AUDIT
    # ---------------------------------------------------------
    print("\n📸 [1] COVER ART AUDIT")
    print("----------------------------------------------------------------------")
    cover_jpg = os.path.join(BOOK_DIR, "cover_ko.jpg")
    cover_png = os.path.join(BOOK_DIR, "cover_ko.png")
    
    target_cover = cover_jpg if os.path.exists(cover_jpg) else cover_png
    if not os.path.exists(target_cover):
        print("❌ CRITICAL: Cover image file not found.")
    else:
        file_size_mb = os.path.getsize(target_cover) / (1024 * 1024)
        with Image.open(target_cover) as img:
            w, h = img.size
            mode = img.mode
            fmt = img.format
            dpi = img.info.get('dpi', (72, 72))

            print(f"  File Path:   {target_cover}")
            print(f"  Dimensions:  {w} x {h} px (Requirement: 2400 x 2400 px)")
            print(f"  File Size:   {file_size_mb:.2f} MB (Requirement: < 5.0 MB)")
            print(f"  Format:      {fmt} (Requirement: JPEG/PNG)")
            print(f"  Color Space: {mode} (Requirement: RGB)")

            cover_issues = []
            if w != 2400 or h != 2400:
                cover_issues.append(f"Dimensions {w}x{h} px fail 2400x2400 px square requirement.")
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
    if not os.path.exists(AUDIO_DIR):
        print(f"❌ CRITICAL: Audio directory not found: {AUDIO_DIR}")
        return

    audio_files = sorted([f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")])
    print(f"Found {len(audio_files)} MP3 tracks in {AUDIO_DIR}\n")

    audio_issues = []
    bitrates = set()
    sample_rates = set()
    channels_set = set()

    for idx, fname in enumerate(audio_files, 1):
        fpath = os.path.join(AUDIO_DIR, fname)
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

        # Special check: Retail sample duration (1 to 5 mins)
        if fname == "sample.mp3":
            if dur_min < 1.0 or dur_min > 5.0:
                track_failed = True
                track_notes.append(f"Retail sample duration {dur_min:.2f} mins outside 1.0-5.0 min limit")

        status_str = "❌ FAIL" if track_failed else "✅ PASS"
        notes_str = f" ({', '.join(track_notes)})" if track_notes else ""

        print(f"  [{idx:02d}] {fname[:28]:<28} | {size_mb:5.1f}MB | {dur_min:5.1f}m | {info['bitrate_kbps']}k | {info['sample_rate']}Hz | Peak: {levels['max_volume_db']}dB | Head: {levels['head_silence_s']:.1f}s | Tail: {levels['tail_silence_s']:.1f}s | {status_str}{notes_str}")

        if track_failed:
            audio_issues.append(f"{fname}: {', '.join(track_notes)}")

    # Check bitrate consistency
    if len(bitrates) > 1:
        audio_issues.append(f"Mixed bitrates detected across tracks: {sorted(list(bitrates))} kbps. All files must match exact same bitrate.")

    # ---------------------------------------------------------
    # 3. AUDIT SUMMARY
    # ---------------------------------------------------------
    print("\n======================================================================")
    print("📊 AUDIT SUMMARY FOR ENCHANTED APRIL")
    print("======================================================================")

    print(f"Total Tracks Audited:    {len(audio_files)}")
    print(f"Bitrate Consistency:     {sorted(list(bitrates))} kbps")
    print(f"Sample Rate Consistency: {sorted(list(sample_rates))} Hz")
    print(f"Channel Consistency:     {sorted(list(channels_set))} channels")
    
    if cover_issues or audio_issues:
        print("\n❌ TOTAL AUDIT RESULT: NON-COMPLIANT (REQUIRES ACTION)")
        print("\nRequired Fixes Summary:")
        for idx, issue in enumerate(cover_issues + audio_issues, 1):
            print(f"  {idx}. {issue}")
    else:
        print("\n✅ TOTAL AUDIT RESULT: FULLY COMPLIANT WITH AUTHORS REPUBLIC")

if __name__ == "__main__":
    run_full_audit()
