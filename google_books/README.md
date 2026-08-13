# Google Books Partner Center Automation Suite

Automated Playwright CDP publishing pipeline for **Google Books Partner Center** (`play.google.com/books/publish/`).

## Architecture & Principles

1. **Zero Auto-Navigation**: Every `fill` script populates its specific page fields and **stops completely**. Scripts will never automatically submit or click Next.
2. **Unified Single-JSON Metadata**: All metadata for a book (Title, Subtitle, Author, Publisher, Description, Categories, EPUB, Cover, Pricing) is saved into **one single JSON file per book** (`notes/google_metadata_<book>_<lang>.json`).
3. **Regular Chrome Integration**: Connects via CDP on Port `9222`.

---

## Suite Scripts Overview

| Script | Purpose | Auto-Submit Behavior |
| :--- | :--- | :--- |
| **`start_google_browser.py`** | Launches regular Google Chrome on port `9222` at Google Books Partner Center. | N/A |
| **`google_0_prepare_metadata.py`** | Generates single-file JSON payload (`google_metadata_<book>_<lang>.json`). | N/A |
| **`google_1_fill_book_info.py`** | Fills Book Info (Title, Subtitle, Author, Publisher, Description, BISACs). | 🛑 **STOPS** for manual review |
| **`google_2_upload_files.py`** | Uploads EPUB manuscript & Cover image. | 🛑 **STOPS** for manual review |
| **`google_3_fill_pricing.py`** | Fills Prices, Currency, and World Distribution Rights. | 🛑 **STOPS** for manual review |
| **`google_nav_next.py`** | Clicks Next/Save *only when manually executed*. | ➡️ Advances 1 step |

---

## Controlled Execution Example

```bash
# 1. Start Regular Google Chrome on Port 9222
python google_books/start_google_browser.py

# 2. Prepare Single-File Metadata (e.g. Gilgamesh KO)
python google_books/google_0_prepare_metadata.py --book gilgamesh --lang ko

# 3. Fill Book Info & STOP for review
python google_books/google_1_fill_book_info.py --book gilgamesh --lang ko

# 4. Advance to Files Tab when ready:
python google_books/google_nav_next.py

# 5. Attach Files (EPUB & Cover) & STOP for review
python google_books/google_2_upload_files.py --book gilgamesh --lang ko

# 6. Advance to Pricing Tab when ready:
python google_books/google_nav_next.py

# 7. Fill Pricing ($3.99 USD) & World Rights & STOP for review
python google_books/google_3_fill_pricing.py --book gilgamesh --lang ko
```
