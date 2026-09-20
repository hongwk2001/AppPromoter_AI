import os
import sys
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

default_path = r"C:\git_repo\TKprof_book\books\blue_castle\cover_ko_audio_2400.jpg"
target_path = sys.argv[1] if len(sys.argv) > 1 else default_path

def check_cover(filepath):
    print(f"Checking cover image: {filepath}")
    if not os.path.exists(filepath):
        print(f"❌ File does not exist: {filepath}")
        return False

    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"  File Size: {file_size_mb:.2f} MB (Requirement: < 5 MB)")

    try:
        with Image.open(filepath) as img:
            width, height = img.size
            format_name = img.format
            mode = img.mode
            dpi = img.info.get('dpi', (72, 72))

            print(f"  Dimensions: {width} x {height} pixels (Requirement: Exactly 2400 x 2400)")
            print(f"  Format: {format_name} (Requirement: JPEG or PNG)")
            print(f"  Color Space / Mode: {mode} (Requirement: RGB)")
            print(f"  DPI / Resolution: {dpi}")

            is_valid = True
            reasons = []

            if width != 2400 or height != 2400:
                is_valid = False
                reasons.append(f"Dimensions are {width}x{height}, required: 2400x2400.")

            if file_size_mb >= 5.0:
                is_valid = False
                reasons.append(f"File size {file_size_mb:.2f} MB exceeds 5 MB limit.")

            if mode not in ["RGB", "RGBA"]:
                is_valid = False
                reasons.append(f"Color mode is {mode}, required: RGB.")

            if is_valid:
                print("\n  ✅ COVER IMAGE MEETS ALL AUTHORS REPUBLIC SPECIFICATIONS!")
            else:
                print("\n  ❌ COVER IMAGE FAILS SPECIFICATIONS:")
                for r in reasons:
                    print(f"     - {r}")

            return is_valid
    except Exception as e:
        print(f"❌ Error opening image: {e}")
        return False

if __name__ == "__main__":
    check_cover(target_path)
