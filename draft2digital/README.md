# Draft2Digital (D2D) Publishing Automation Suite

Automated Playwright CDP publishing pipeline for Draft2Digital ebooks.

## Scripts Overview

1. **`start_d2d_browser.py`**: Launches Playwright Chromium on CDP port `9222` with a persistent profile.
2. **`inspect_d2d_form.py`**: Connects via CDP and extracts form field schemas (`d2d_form_schema_<step>.json`).
3. **`prepare_d2d_metadata.py`**: Prepares JSON metadata payloads (`d2d_payload_<book>_<lang>.json`) with title, author, publisher, content rating, categories, and file paths.
4. **`automate_d2d_upload.py`**: Automates **Step 1 (Metadata)**: Title, Author, Publisher, Language, Content Rating, Search Terms (with Enter keypresses), 3+ BISACs, and Cover Upload.
5. **`automate_d2d_step2.py`**: Automates **Step 2 (Ebook Details)**: Manuscript EPUB Upload, Short Description, CKEditor 5 Description (`setData`), Non-Author Contributors (`TKPROF LLC` as Translator & Editor), and Free D2D ISBN.
6. **`automate_d2d_step3.py`**: Automates **Step 3 (Pricing & Distribution)**: Digital Price, Library Price, 38+ Supported Distribution Channels/Stores.
7. **`click_save_and_continue.py`**: Navigates between publishing steps.
8. **`save_store_preferences.py`**: Checks "Remember my store preferences".
9. **`capture_d2d_screenshot.py`**: Captures CDP screenshots for visual verification.

## Usage Example

```bash
# 1. Start Browser
python draft2digital/start_d2d_browser.py

# 2. Run Step 1 (Shared Metadata & Cover Upload)
python draft2digital/automate_d2d_upload.py --book tono_bungay --lang ko

# 3. Run Step 2 (Ebook Details & EPUB Upload)
python draft2digital/automate_d2d_step2.py --book tono_bungay --lang ko

# 4. Run Step 3 (Pricing & Rights)
python draft2digital/automate_d2d_step3.py --price 3.99 --library-price 9.99
```
