import os
import sys
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BOOK_DIR = r"C:\git_repo\TKprof_book\books\the_enchanted_april"

def get_duration(filepath):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def prepare_ready_tracks(audio_dir_name="final_audio_ko", ready_dir_name="final_audio_ko_ready", max_mb=30.0):
    src_dir = os.path.join(BOOK_DIR, audio_dir_name)
    out_dir = os.path.join(BOOK_DIR, ready_dir_name)
    os.makedirs(out_dir, exist_ok=True)

    all_files = sorted([f for f in os.listdir(src_dir) if f.endswith(".mp3")])
    ready_files = []

    print(f"Processing {len(all_files)} audio files from {src_dir} (threshold {max_mb} MB)...")
    for filename in all_files:
        src = os.path.join(src_dir, filename)
        size_mb = os.path.getsize(src) / (1024 * 1024)

        if size_mb <= max_mb:
            dst = os.path.join(out_dir, filename)
            if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
                with open(src, "rb") as rf, open(dst, "wb") as wf:
                    wf.write(rf.read())
            ready_files.append(dst)
        else:
            duration = get_duration(src)
            num_parts = int(size_mb // max_mb) + 1
            part_duration = duration / float(num_parts)

            print(f" Splitting {filename} ({size_mb:.1f} MB, {duration:.1f}s) into {num_parts} sub-parts...")

            for p_idx in range(num_parts):
                part_name = filename.replace(".mp3", f"_part{p_idx+1}.mp3")
                part_path = os.path.join(out_dir, part_name)

                start_time = p_idx * part_duration
                if p_idx == num_parts - 1:
                    cmd = ["ffmpeg", "-y", "-ss", str(start_time), "-i", src, "-c", "copy", part_path]
                else:
                    cmd = ["ffmpeg", "-y", "-ss", str(start_time), "-i", src, "-t", str(part_duration), "-c", "copy", part_path]

                subprocess.run(cmd, capture_output=True, check=True)
                ready_files.append(part_path)

    print(f"✅ Total tracks ready in {out_dir}: {len(ready_files)}")
    return ready_files

if __name__ == "__main__":
    prepare_ready_tracks("final_audio_ko", "final_audio_ko_ready", 30.0)
    prepare_ready_tracks("final_audio", "final_audio_ready", 30.0)
