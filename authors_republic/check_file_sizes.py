import os
import sys

audio_dir = r"C:\git_repo\TKprof_book\books\blue_castle\final_audio_ko"

large_files = []
for f in os.listdir(audio_dir):
    if f.endswith(".mp3"):
        fp = os.path.join(audio_dir, f)
        size_mb = os.path.getsize(fp) / (1024 * 1024)
        if size_mb > 45.0:
            large_files.append((f, size_mb))

print(f"Total files > 45MB in {audio_dir}: {len(large_files)}")
for f, size in sorted(large_files, key=lambda x: x[1], reverse=True):
    print(f"  {f}: {size:.2f} MB")
