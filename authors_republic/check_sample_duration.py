import os
import subprocess

sample_file = r"C:\git_repo\TKprof_book\books\blue_castle\final_audio_ko_ready\final_track_01.mp3"

cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", sample_file]
res = subprocess.run(cmd, capture_output=True, text=True, check=True)
duration_sec = float(res.stdout.strip())
duration_min = duration_sec / 60.0

print(f"File: {os.path.basename(sample_file)}")
print(f"Duration: {duration_sec:.1f} seconds ({duration_min:.2f} minutes)")
