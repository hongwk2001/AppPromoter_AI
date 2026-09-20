"""
upload_scaramouche_series.py
Automates metadata generation and autofill for Scaramouche Books 1, 2, and 3.
SAFETY GUARANTEED: Stops before submitting the final publish button.
"""

import os
import sys
import argparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from d2d_0_prepare_metadata import prepare_unified_metadata

BOOKS = ["scaramouche_book1", "scaramouche_book2", "scaramouche_book3"]

def process_series(lang="ko", port=9222):
    print("\n=======================================================")
    print("🚀 SCARAMOUCHE SERIES DRAFT PUBLISHING AUTOMATION")
    print("   SAFETY GUARD ACTIVE: Will NOT click final publish button.")
    print("=======================================================\n")

    for b_key in BOOKS:
        print(f"\n-------------------------------------------------------")
        print(f"📦 Processing: {b_key} ({lang.upper()})")
        print(f"-------------------------------------------------------")
        
        data = prepare_unified_metadata(b_key, lang)
        if not data:
            print(f"❌ Failed to prepare metadata for {b_key}")
            continue

        print(f"✅ Metadata ready for {data['step1_metadata']['title']}")
        print(f"   EPUB: {data['step2_details']['epub_path']}")
        print(f"   Cover: {data['step1_metadata']['cover_image_path']}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaramouche Series D2D Batch Processor")
    parser.add_argument("--lang", type=str, default="ko", choices=["ko", "en"])
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    process_series(lang=args.lang, port=args.port)
