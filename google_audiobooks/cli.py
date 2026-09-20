import os
import sys
import time
import json
import argparse
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")
sys.path.insert(0, os.path.join(BASE_DIR, "modules"))

def load_google_metadata(book_name="gilgamesh", lang="ko"):
    meta_path = os.path.join(NOTES_DIR, f"google_audio_metadata_{book_name}_{lang}.json")
    if not os.path.exists(meta_path):
        from google_audio_0_prepare_metadata import prepare_audiobook_metadata
        return prepare_audiobook_metadata(book_name, lang)
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_book_base_url(page):
    if "#book/" in page.url:
        fragment = page.url.split("#")[1]
        book_id = fragment.split(";")[0]
        return page.url.split("#")[0] + "#" + book_id + ";jc=true"
    return ""

def run_cli_command(command, book_name="gilgamesh", lang="ko", port=9222):
    meta = load_google_metadata(book_name, lang)
    book_info = meta.get("book_info", {})
    contributors = meta.get("contributors", [])
    cf = meta.get("content_files", {})

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:
            print(f"❌ Error connecting to Chrome on port {port}: {e}")
            return

        pages = [pg for pg in browser.contexts[0].pages if "#book/" in pg.url or "publish" in pg.url or "google" in pg.url]
        page = pages[0] if pages else browser.contexts[0].pages[0]
        print(f"Active Page URL: {page.url}")

        book_base = get_book_base_url(page)

        if command == "fill-about":
            from page_about import fill_about_page
            if "info/about" not in page.url and book_base:
                page.goto(f"{book_base}/info/about")
                time.sleep(2)
            fill_about_page(page, book_info)

        elif command == "fill-genres":
            from page_genres import fill_genres_page
            if "info/genres" not in page.url and book_base:
                page.goto(f"{book_base}/info/genres")
                time.sleep(2)
            fill_genres_page(page, book_info, lang)

        elif command == "fill-contributors":
            from page_contributors import fill_contributors_page
            if "info/contributors" not in page.url and book_base:
                page.goto(f"{book_base}/info/contributors")
                time.sleep(2)
            fill_contributors_page(page, contributors)

        elif command == "upload-content":
            from page_content import upload_content_page
            if "content" not in page.url and book_base:
                page.goto(f"{book_base}/content")
                time.sleep(2)
            upload_content_page(page, cf)

        elif command == "fill-pricing":
            from page_pricing import fill_pricing_page
            if "pricing" not in page.url and book_base:
                page.goto(f"{book_base}/pricing")
                time.sleep(2)
            fill_pricing_page(page, price="9.99")

        elif command == "fill-all":
            from page_about import fill_about_page
            from page_genres import fill_genres_page
            from page_contributors import fill_contributors_page
            from page_content import upload_content_page
            from page_pricing import fill_pricing_page

            if book_base:
                page.goto(f"{book_base}/info/about")
                time.sleep(2)
                fill_about_page(page, book_info)

                page.goto(f"{book_base}/info/genres")
                time.sleep(2)
                fill_genres_page(page, book_info, lang)

                page.goto(f"{book_base}/info/contributors")
                time.sleep(2)
                fill_contributors_page(page, contributors)

                page.goto(f"{book_base}/content")
                time.sleep(2)
                upload_content_page(page, cf)

                page.goto(f"{book_base}/pricing")
                time.sleep(2)
                fill_pricing_page(page, price="9.99")

                page.goto(f"{book_base}/review")
                time.sleep(2.5)

            print("\n🎉 Modular Fill-All complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Play Books Modular Automation CLI Router")
    parser.add_argument("command", choices=["fill-about", "fill-genres", "fill-contributors", "upload-content", "fill-pricing", "fill-all"])
    parser.add_argument("--book", default="gilgamesh")
    parser.add_argument("--lang", default="ko")
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    run_cli_command(args.command, args.book, args.lang, args.port)
