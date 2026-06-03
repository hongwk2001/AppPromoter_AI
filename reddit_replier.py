# I'm thinking to make email aggregator that can help me clean up emails. 
# let's see if it will come all right.
import os
import sys
import json
import argparse
import webbrowser
import subprocess
import requests
import re
import urllib.parse
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import scrolledtext
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def copy_to_clipboard(text):
    """Copies text to clipboard on Windows using built-in clip command."""
    try:
        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, close_fds=True)
        process.communicate(input=text.encode('utf-8'))
        print("[OK] Draft reply copied to clipboard!")
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False

def save_to_few_shots(few_shots_path, post, finalized_reply):
    """Appends the matched post details and approved reply to the few-shots JSONL file."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(few_shots_path)), exist_ok=True)
        
        entry = {
            'post_title': post['title'],
            'post_content': post['content'],
            'post_url': post['url'],
            'subreddit': post['subreddit'],
            'approved_reply': finalized_reply
        }
        
        with open(few_shots_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
        print(f"[OK] Saved approved reply to few-shots history: '{few_shots_path}'")
    except Exception as e:
        print(f"Error saving to few-shots: {e}")

def save_to_skipped(skipped_posts_path, post):
    """Appends the matched post details to the skipped posts history JSONL file for future revisit."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(skipped_posts_path)), exist_ok=True)
        
        with open(skipped_posts_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(post, ensure_ascii=False) + '\n')
            
        print(f"[OK] Saved post to skipped list: '{skipped_posts_path}'")
    except Exception as e:
        print(f"Error saving to skipped posts: {e}")

def load_few_shots(few_shots_path, max_examples=3):
    """Loads past few-shot examples from the JSONL history file."""
    examples = []
    if not few_shots_path or not os.path.exists(few_shots_path):
        return examples
        
    try:
        with open(few_shots_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))
        return examples[-max_examples:]
    except Exception as e:
        print(f"Error loading few-shots: {e}")
        return []

def load_processed_post_keys(few_shots_path, skipped_posts_path):
    """Loads URLs and Titles of posts that have already been replied to or skipped."""
    processed = set()
    
    # Load from few shots
    if few_shots_path and os.path.exists(few_shots_path):
        try:
            with open(few_shots_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        title = data.get('post_title')
                        url = data.get('post_url')
                        if title:
                            processed.add(title.strip().lower())
                        if url:
                            processed.add(url.strip().lower())
        except Exception:
            pass
            
    # Load from skipped posts
    if skipped_posts_path and os.path.exists(skipped_posts_path):
        try:
            with open(skipped_posts_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        url = data.get('url')
                        title = data.get('title')
                        if url:
                            processed.add(url.strip().lower())
                        if title:
                            processed.add(title.strip().lower())
        except Exception:
            pass
            
    return processed

def clean_html(html_text):
    """Helper to strip HTML tags and decode basic entities from RSS content."""
    if not html_text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', html_text)
    text = (text.replace('&lt;', '<')
                .replace('&gt;', '>')
                .replace('&amp;', '&')
                .replace('&quot;', '"')
                .replace('&#39;', "'")
                .replace('&nbsp;', ' '))
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def edit_with_popup(post_details, initial_draft):
    """Opens a Tkinter popup displaying both the original post and the editable draft reply."""
    root = tk.Tk()
    root.title("Review & Edit Draft Reply")
    root.geometry("800x650")
    root.configure(bg='#1e293b')
    
    # 1. Original Reddit Post Section (Read-Only)
    post_frame = tk.LabelFrame(root, text=f" Original Post (r/{post_details['subreddit']} by u/{post_details['author']}) ", 
                               bg='#1e293b', fg='#3b82f6', font=("Arial", 10, "bold"), bd=1, relief=tk.SOLID)
    post_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
    
    title_label = tk.Label(post_frame, text=f"Title: {post_details['title']}", bg='#1e293b', fg='#f8fafc', 
                           font=("Arial", 10, "bold"), anchor="w", justify=tk.LEFT)
    title_label.pack(padx=10, pady=5, fill=tk.X)
    
    post_text = scrolledtext.ScrolledText(post_frame, height=8, bg='#0f172a', fg='#cbd5e1', font=("Arial", 10))
    post_text.insert(tk.INSERT, post_details['content'])
    post_text.configure(state='disabled')
    post_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    # 2. Editable Draft Reply Section
    draft_frame = tk.LabelFrame(root, text=" Editable Draft Reply ", 
                                bg='#1e293b', fg='#10b981', font=("Arial", 10, "bold"), bd=1, relief=tk.SOLID)
    draft_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
    
    txt = scrolledtext.ScrolledText(draft_frame, height=10, bg='#0f172a', fg='#f8fafc', 
                                     insertbackground='#f8fafc', font=("Consolas", 10))
    txt.insert(tk.INSERT, initial_draft)
    txt.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    final_text = [initial_draft]
    is_saved = [False]
    
    def save_and_close():
        final_text[0] = txt.get("1.0", tk.END).strip()
        is_saved[0] = True
        root.destroy()
        
    def cancel_and_close():
        root.destroy()
        
    btn_frame = tk.Frame(root, bg='#1e293b')
    btn_frame.pack(pady=15)
    
    save_btn = tk.Button(btn_frame, text="Save & Done", command=save_and_close, 
                         bg='#10b981', fg='white', width=14, relief=tk.FLAT,
                         activebackground='#059669', activeforeground='white', font=("Arial", 10, "bold"))
    save_btn.pack(side=tk.LEFT, padx=15)
    
    cancel_btn = tk.Button(btn_frame, text="Cancel", command=cancel_and_close, 
                           bg='#475569', fg='white', width=14, relief=tk.FLAT,
                           activebackground='#334155', activeforeground='white', font=("Arial", 10))
    cancel_btn.pack(side=tk.LEFT, padx=15)
    
    txt.focus_set()
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    root.mainloop()
    return final_text[0], is_saved[0]

def fetch_reddit_posts(subreddits, keywords, limit=15):
    """Fetches matched posts from target subreddits using Reddit's search RSS to maximize relevance and volume."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    
    matched_posts = []
    print(f"\nSearching subreddits: {', '.join(subreddits)} for keywords: {', '.join(keywords)}...")
    
    for sub in subreddits:
        for keyword in keywords:
            query = urllib.parse.quote(keyword)
            url = f"https://www.reddit.com/r/{sub}/search.rss?q={query}&restrict_sr=on&sort=new&limit={limit}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
                    
                    entries = root.findall('atom:entry', namespaces)
                    for entry in entries:
                        title_el = entry.find('atom:title', namespaces)
                        title = title_el.text if title_el is not None else ""
                        
                        content_el = entry.find('atom:content', namespaces)
                        raw_content = content_el.text if content_el is not None else ""
                        content = clean_html(raw_content)
                        
                        link_el = entry.find('atom:link', namespaces)
                        post_url = link_el.attrib.get('href', '') if link_el is not None else ""
                        
                        author_name = "unknown"
                        author_el = entry.find('atom:author', namespaces)
                        if author_el is not None:
                            name_el = author_el.find('atom:name', namespaces)
                            if name_el is not None:
                                author_name = name_el.text.replace("/u/", "")
                                
                        id_el = entry.find('atom:id', namespaces)
                        post_id = id_el.text if id_el is not None else post_url
                        
                        full_text = f"{title} {content}".lower()
                        matches = [kw for kw in keywords if kw.lower() in full_text]
                        
                        if matches:
                            matched_posts.append({
                                'id': post_id,
                                'title': title,
                                'content': content,
                                'author': author_name,
                                'subreddit': sub,
                                'url': post_url,
                                'matched_keywords': list(set(matches))
                            })
                else:
                    if response.status_code != 429:
                        print(f"Warning: Failed search in r/{sub} for '{keyword}'. Status: {response.status_code}")
            except Exception as e:
                pass
            
    seen = set()
    unique_posts = []
    for p in matched_posts:
        if p['id'] not in seen:
            seen.add(p['id'])
            unique_posts.append(p)
            
    return unique_posts

def generate_reply_gemini(post, kb_content, few_shots, model="gemini-2.5-flash"):
    """Uses Gemini API to synthesize a response."""
    api_key = GEMINI_API_KEY or "AIzaSyDr5FH2c0HWbTgcRRFhRlX72a5jMyC50CE"
    client = genai.Client(api_key=api_key)
    
    system_instruction = (
        "You are an expert product assistant and community contributor. "
        "Your task is to draft a helpful, expert reply to a Reddit user's question.\n\n"
        "CRITICAL GUIDELINES:\n"
        "1. Write in a helpful, conversational, and direct tone. Never sound like a generic corporate AI or a sales rep.\n"
        "2. Directly answer their question first with high-value technical/practical advice based on the Knowledge Base.\n"
        "3. Only mention/link the product naturally at the end if it is directly relevant and provides a genuine solution to their problem. "
        "Avoid salesy language (do not use phrases like 'game changer', 'revolutionary', 'look no further').\n"
        "4. Keep the response extremely concise. The reply MUST be shorter in length than the original user post question.\n"
        "5. Output ONLY the reply text, no markdown headers or other metadata."
    )
    
    few_shots_block = ""
    if few_shots:
        few_shots_block += "--- EXAMPLES OF YOUR PREVIOUSLY APPROVED REPLIES (MATCH THIS STYLE AND TONE) ---\n"
        for idx, ex in enumerate(few_shots, 1):
            few_shots_block += (
                f"Example {idx}:\n"
                f"Reddit Post Title: {ex.get('post_title')}\n"
                f"Reddit Post Content: {ex.get('post_content')}\n"
                f"Your Approved Reply:\n{ex.get('approved_reply')}\n"
                f"-----------\n"
            )
            
    prompt = (
        f"--- KNOWLEDGE BASE (SOURCE OF TRUTH) ---\n"
        f"{kb_content}\n\n"
        f"{few_shots_block}\n"
        f"--- REDDIT POST TO REPLY TO ---\n"
        f"Subreddit: r/{post['subreddit']}\n"
        f"Title: {post['title']}\n"
        f"Content:\n{post['content']}\n\n"
        f"Generate a customized, natural reply following the system instructions above."
    )
    
    import time
    attempts = 4
    response = None
    for attempt in range(attempts):
        try:
            response = client.models.generate_content(
                model=model,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                ),
                contents=prompt,
            )
            break
        except Exception as e:
            if "503" in str(e) and attempt < attempts - 1:
                print(f"Gemini servers busy (503). Retrying in 6 seconds (attempt {attempt+1}/{attempts})...")
                time.sleep(6)
            else:
                print(f"Error calling Gemini: {e}")
                return None
                
    if response and response.text:
        disclaimer = "\n\n*(Drafted with the assistance of Gemini AI)*"
        return response.text.strip() + disclaimer
    return None

def generate_reply_ollama(post, kb_content, few_shots, model="gemma2", api_url="http://localhost:11434"):
    """Uses a local Ollama instance (e.g. running gemma2) to generate a response."""
    system_instruction = (
        "You are an expert product assistant and community contributor. "
        "Your task is to draft a helpful, expert reply to a Reddit user's question.\n\n"
        "CRITICAL GUIDELINES:\n"
        "1. Write in a helpful, conversational, and direct tone. Never sound like a generic corporate AI or a sales rep.\n"
        "2. Directly answer their question first with high-value technical/practical advice based on the Knowledge Base.\n"
        "3. Only mention/link the product naturally at the end if it is directly relevant and provides a genuine solution to their problem. "
        "Avoid salesy language.\n"
        "4. Keep the response extremely concise. The reply MUST be shorter in length than the original user post question.\n"
        "5. Output ONLY the reply text, no headers or metadata."
    )
    
    few_shots_block = ""
    if few_shots:
        few_shots_block += "--- EXAMPLES OF YOUR PREVIOUSLY APPROVED REPLIES (MATCH THIS STYLE AND TONE) ---\n"
        for idx, ex in enumerate(few_shots, 1):
            few_shots_block += (
                f"Example {idx}:\n"
                f"Reddit Post Title: {ex.get('post_title')}\n"
                f"Reddit Post Content: {ex.get('post_content')}\n"
                f"Your Approved Reply:\n{ex.get('approved_reply')}\n"
                f"-----------\n"
            )
            
    prompt = (
        f"{system_instruction}\n\n"
        f"--- KNOWLEDGE BASE (SOURCE OF TRUTH) ---\n"
        f"{kb_content}\n\n"
        f"{few_shots_block}\n"
        f"--- REDDIT POST TO REPLY TO ---\n"
        f"Subreddit: r/{post['subreddit']}\n"
        f"Title: {post['title']}\n"
        f"Content:\n{post['content']}\n\n"
        f"Generate a customized, natural reply following the instructions above."
    )
    
    try:
        response = requests.post(
            f"{api_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3
                }
            },
            timeout=120
        )
        if response.status_code == 200:
            reply_text = response.json().get("response", "").strip()
            disclaimer = f"\n\n*(Drafted with the assistance of {model} via Ollama)*"
            return reply_text + disclaimer
        else:
            print(f"Ollama returned error status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error calling local Ollama server: {e}")
        return None

def interactive_review(posts, kb_content, few_shots_path, skipped_posts_path, provider="gemini", model_name=None):
    """CLI dashboard for reviewing and posting replies."""
    total = len(posts)
    print(f"\nFound {total} matching posts to review.")
    
    few_shots = load_few_shots(few_shots_path)
    
    for i, post in enumerate(posts, 1):
        print("\n" + "="*80)
        print(f" POST {i}/{total} | r/{post['subreddit']} | Matches: {post['matched_keywords']}")
        print(f" Title:  {post['title']}")
        print(f" Author: u/{post['author']}")
        print(f" URL:    {post['url']}")
        print("-"*80)
        content_snippet = post['content'][:400] + ("..." if len(post['content']) > 400 else "")
        print(content_snippet or "[No body text]")
        print("="*80)
        
        while True:
            print("\nActions: [d]raft reply & open editor | [s]kip | [q]uit")
            choice = input("Select action: ").strip().lower()
            
            if choice == 's':
                save_to_skipped(skipped_posts_path, post)
                break
            elif choice == 'q':
                print("Exiting review dashboard.")
                return
            elif choice == 'd':
                draft = None
                current_provider = provider
                current_model = model_name
                while True:
                    print(f"\nGenerating draft reply using {current_provider} ({current_model or 'default'})...")
                    if current_provider == "ollama":
                        model = current_model or "gemma2"
                        draft = generate_reply_ollama(post, kb_content, few_shots, model=model)
                    else:
                        model = current_model or "gemini-2.5-flash"
                        draft = generate_reply_gemini(post, kb_content, few_shots, model=model)
                        
                    if draft:
                        break
                        
                    print("\n[ERROR] Failed to generate draft (timeout or server error).")
                    print("Actions: [r]etry current | [g]emini fallback | [o]llama fallback | [s]kip | [q]uit")
                    err_choice = input("Select action: ").strip().lower()
                    if err_choice == 'r':
                        continue
                    elif err_choice == 'g':
                        current_provider = "gemini"
                        current_model = "gemini-2.5-flash"
                        continue
                    elif err_choice == 'o':
                        current_provider = "ollama"
                        current_model = model_name if (model_name and "gemma4" in model_name) else "gemma4:e2b"
                        continue
                    elif err_choice == 's':
                        save_to_skipped(skipped_posts_path, post)
                        draft = None
                        break
                    elif err_choice == 'q':
                        print("Exiting review dashboard.")
                        return
                    else:
                        print("Invalid input. Skipping post.")
                        save_to_skipped(skipped_posts_path, post)
                        draft = None
                        break
                
                if not draft:
                    break
                
                edited_draft, saved = edit_with_popup(post, draft)
                
                if saved:
                    copy_to_clipboard(edited_draft)
                    save_to_few_shots(few_shots_path, post, edited_draft)
                    few_shots = load_few_shots(few_shots_path)
                    webbrowser.open(post['url'])
                else:
                    save_to_skipped(skipped_posts_path, post)
                    print("Edit cancelled. Post saved to skipped list.")
                break
            else:
                print("Invalid input. Please choose d, s, or q.")

def main():
    parser = argparse.ArgumentParser(description="KB-Driven Reddit Replier Dashboard")
    parser.add_argument("--app", default="npc-aggregator", choices=["npc-aggregator", "golf-swing-ai"],
                        help="Application key defined in config.json")
    parser.add_argument("--limit", type=int, default=15, help="Max search result limit per keyword")
    parser.add_argument("--provider", default="gemini", choices=["gemini", "ollama"],
                        help="LLM provider to use (gemini or local ollama)")
    parser.add_argument("--model", default=None,
                        help="Model name (e.g. gemma2 for Ollama or gemini-2.5-flash for Gemini)")
    args = parser.parse_args()
    
    # Load config
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        
    app_config = config["apps"].get(args.app)
    if not app_config:
        print(f"Error: app key '{args.app}' not found in config.json")
        sys.exit(1)
        
    subreddits = app_config.get("reddit_subreddits", [])
    keywords = app_config.get("reddit_keywords", [])
    kb_file = app_config.get("kb_file", "")
    few_shots_file = app_config.get("few_shots_file", "")
    skipped_posts_file = app_config.get("skipped_posts_file", "")
    
    if not subreddits or not keywords or not kb_file or not few_shots_file or not skipped_posts_file:
        print(f"Error: Missing configurations for '{args.app}' in config.json.")
        sys.exit(1)
        
    # Read knowledge base
    if not os.path.exists(kb_file):
        print(f"Error: Knowledge base file '{kb_file}' not found.")
        sys.exit(1)
        
    with open(kb_file, "r", encoding="utf-8") as f:
        kb_content = f.read()
        
    # Fetch posts
    posts = fetch_reddit_posts(subreddits, keywords, limit=args.limit)
    
    if not posts:
        print("\nNo matching posts found. Modify keywords or try again later.")
        return
        
    # Filter out already processed (replied or skipped) posts
    processed_keys = load_processed_post_keys(few_shots_file, skipped_posts_file)
    filtered_posts = []
    for p in posts:
        url_key = p['url'].strip().lower()
        title_key = p['title'].strip().lower()
        if url_key not in processed_keys and title_key not in processed_keys:
            filtered_posts.append(p)
            
    if not filtered_posts:
        print("\nAll matching posts have already been reviewed (replied or skipped).")
        return
        
    # Start review flow
    interactive_review(filtered_posts, kb_content, few_shots_file, skipped_posts_file, 
                       provider=args.provider, model_name=args.model)

if __name__ == "__main__":
    main()
