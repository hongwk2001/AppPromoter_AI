import os
import sys
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

audio_dir = r"C:\git_repo\TKprof_book\books\blue_castle\final_audio_ko_ready"
src_track = os.path.join(audio_dir, "final_track_01.mp3")
sample_out = os.path.join(audio_dir, "sample_retail.mp3")

print(f"Creating 3-minute Retail Sample track from {os.path.basename(src_track)}...")

# Trim exactly 3 minutes (180 seconds)
cmd = ["ffmpeg", "-y", "-ss", "0", "-i", src_track, "-t", "180", "-c", "copy", sample_out]
res = subprocess.run(cmd, capture_output=True, check=True)

# Verify duration
cmd_probe = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", sample_out]
res_probe = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
dur = float(res_probe.stdout.strip())

print(f"✅ Created Retail Sample: {sample_out}")
print(f"   Duration: {dur:.1f} seconds ({dur/60.0:.2f} minutes)")
