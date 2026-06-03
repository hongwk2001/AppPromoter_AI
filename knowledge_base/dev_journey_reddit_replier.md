# Building a KB-Driven Reddit Outreach Dashboard

We built a custom local **outreach dashboard** to scan Reddit, draft context-rich responses via LLMs based on product knowledge bases, and quickly reply manually. Here is the architecture.

---

## 1. The Pain: Reddit's HTTP 403 Blocks
Reddit blocks standard API requests from scripts. 

![403 Error Blocks](error_403.png)

**The Fix**: We scrape posts via Reddit's public Atom RSS search feeds with a browser User-Agent, bypassing the blocks completely.

---

## 2. Interactive CLI & Deduplication
To prevent duplicate replies and spamming:
* **Deduplication Filter**: Automatically hides posts you already skipped or replied to.
* **Dynamic Feedback**: Appends approved/edited responses to a few-shots history file to align future drafts with your tone.

![CLI Review Interface](cli_menu.png)

---

## 3. Gemini Token Limits & The Local Gemma Transition
Initially, we ran everything through the Gemini API, but we hit the token/rate limits when loading large chunks of subreddit context.

![Gemini Token Limit Error](gemini_token_limit.png)

To solve this, we tried running Gemma 2 locally using **Ollama** (`gemma4:e2b`), which was surprisingly easy to set up.
* **Timeout Fix**: Increased the API connection timeout to **120s** to allow the 7.2 GB local model to load into memory.
* **One-Click Fallback**: Added a fallback option to switch to the **Gemini Cloud** (`gemini-2.5-flash`) if the local model times out.

---

## 4. Human-in-the-Loop Tkinter Popup
Selecting `d` (draft) opens a dual-panel popup editor built with `tkinter`:
* **Top (Read-Only)**: Displays the original Reddit post for context.
* **Bottom (Editable)**: Displays the AI-generated reply.
* **Save & Done**: Copies text to clipboard, logs the few-shot example, and opens the browser thread.

![Tkinter Side-by-Side Editor Window](reddit_review_screenshot.png)

<!-- I'm thinking to make email aggregator that can help me clean up emails. let's see if it will come all right. -->
