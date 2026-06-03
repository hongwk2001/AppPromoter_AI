# Social Media Publishing Guide & Lessons Learned

This document outlines the UI quirks and operational guidelines for automating video uploads to Instagram and TikTok using Playwright.

## 📸 Instagram Publishing

### 1. Session Storage (`instagram_session.json`)
* The script saves login state to `instagram_session.json` in the root folder.
* Always check if the file exists to bypass the login & 2FA screens on subsequent uploads.

### 2. Post Creation Flow & Sub-menu Workaround
* When clicking the **"Create" (+)** button on Instagram web, it opens a sub-menu instead of the post creator immediately.
* **Solution:** The script must click **"Create"**, wait for 2 seconds, and then click **"Post"** (selector: `text="Post"`, `span:has-text("Post")`, or `svg[aria-label="Post"]`).
* If a popup modal (like "Turn on Notifications" or "Save Info") blocks the UI:
  1. Click **Create** > **Post** manually in the browser.
  2. The script will automatically detect the file input once it's visible.

### 3. Publishing Confirmation
* At the final screen, the script attempts to locate and click the **"Share"** button. If the button click is intercepted or fails (due to overlay elements), you must click **"Share"** manually in the browser modal to complete the post.
* **Closing the Python Job:** Once the video has been successfully selected and uploaded, you can safely close/terminate the Python command or job in your terminal. You can finish the final click on your own without needing the script to run to completion.

---

## 🎵 TikTok Publishing

### 1. Session Storage (`tiktok_session.json`)
* The script saves login state to `tiktok_session.json` in the root folder.
* Since TikTok has strict bot-detection (slide puzzles/captchas), the user **must manually log in and complete 2FA** on the first run.
* Once logged in, the session is saved, and subsequent runs bypass the login page.

### 2. Video Upload & Post
* The script navigates to `tiktok.com/tiktokstudio/upload`, uploads the `final_shorts.mp4`, and types the caption.
* Review the settings and click **"Post"** in the browser window to publish.

---

## 🤖 Reddit Automation & Community Outreach

### 1. Bypassing HTTP 403 blocks (RSS/Atom Feeds)
* Reddit aggressively blocks standard API `.json` requests from non-browser/script user-agents.
* **Solution**: Scrape posts via Reddit's public Atom RSS feeds (e.g. `https://www.reddit.com/r/{subreddit}/new.rss` or search feeds `https://www.reddit.com/r/{subreddit}/search.rss?q={query}`) and parse them using Python's built-in `xml.etree.ElementTree`. Use a realistic browser User-Agent.

### 2. Local LLM (Ollama) Execution Workarounds
* Large local models (e.g. `gemma4:e2b` (7.2 GB) or `gemma2`) can take a significant amount of time to load into RAM/VRAM on initial token generation.
* **Solution**: Always set a high HTTP request timeout (e.g., `timeout=120` or higher) on client calls to local Ollama endpoints to prevent standard 30s HTTP read timeouts.

### 3. Progressive History Filters (Deduplication)
* To prevent duplicate reviews on subsequent script execution, maintain history files for processed posts (`few_shots_*.jsonl` and `skipped_posts_*.jsonl`).
* Filter fetched posts using these history files (matching by URL or Title) before presenting them to the user.

### 4. Human-In-The-Loop GUI Popup Editor
* For CLI tools requiring text verification, launching a simple popup editor using Python's standard `tkinter` library provides a much cleaner editing interface than inline terminal inputs.
* Side-by-side or top-and-bottom layouts displaying the original post content next to the editable draft draft keep all necessary context in a single view.
