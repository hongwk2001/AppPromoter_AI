import os
import glob
import json

def sort_key(p):
    fname = os.path.basename(p).lower()
    if fname == "opening_credits.mp3" or fname == "opening.mp3":
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

audio_dir = r"C:\git_repo\TKprof_book\books\beowulf\final_audio_ko"
files = glob.glob(os.path.join(audio_dir, "*.mp3"))
files.sort(key=sort_key)
fnames = [os.path.basename(f) for f in files]
print(f"Total sorted files: {len(fnames)}")
for idx, fn in enumerate(fnames, 1):
    print(f"  {idx:02d}. {fn}")

