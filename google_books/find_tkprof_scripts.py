import os
import glob

tk_dir = r"C:\git_repo\TKprof_book"
print(f"--- Python Scripts in {tk_dir} ---")
for root, dirs, files in os.walk(tk_dir):
    if "venv" in root or ".git" in root or "node_modules" in root:
        continue
    for f in files:
        if f.endswith(".py") and ("upload" in f.lower() or "d2d" in f.lower() or "google" in f.lower() or "prepare" in f.lower() or "audio" in f.lower()):
            print(os.path.join(root, f))
