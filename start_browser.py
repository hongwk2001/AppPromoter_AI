"""
start_browser.py
General-purpose browser launcher for automated publishing platforms (Authors Republic, Draft2Digital, Google Books, KDP).
Launches Chrome with remote debugging on port 9222.
"""

import os
import sys
import argparse
import subprocess
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PLATFORM_URLS = {
    "ar": "https://www.authorsrepublic.com/the-republic/projects/new-project",
    "authors_republic": "https://www.authorsrepublic.com/the-republic/projects/new-project",
    "d2d": "https://www.draft2digital.com/book/",
    "draft2digital": "https://www.draft2digital.com/book/",
    "google": "https://play.google.com/books/publish/",
    "google_books": "https://play.google.com/books/publish/",
    "kdp": "https://kdp.amazon.com/"
}

DEFAULT_PROFILE_DIR = r"C:\tmp\chrome_dev_user"

def is_cdp_active(port=9222):
    try:
        url = f"http://127.0.0.1:{port}/json/version"
        with urllib.request.urlopen(url, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False

def find_chrome():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def launch_browser(platform="authors_republic", target_url=None, port=9222, profile_dir=DEFAULT_PROFILE_DIR):
    if target_url is None:
        target_url = PLATFORM_URLS.get(platform.lower(), PLATFORM_URLS["authors_republic"])

    os.makedirs(profile_dir, exist_ok=True)

    if is_cdp_active(port):
        print(f"✅ Chrome CDP is already active on port {port}.")
        print(f"  Target URL: {target_url}")
        return True

    chrome_path = find_chrome()
    if not chrome_path:
        print("❌ Could not find Google Chrome executable.")
        return False

    cmd = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir}",
        target_url
    ]

    print(f"🚀 Launching Chrome on CDP port {port}...")
    print(f"  Executable: {chrome_path}")
    print(f"  Profile:    {profile_dir}")
    print(f"  URL:        {target_url}")

    proc = subprocess.Popen(cmd, creationflags=0x00000010)
    print(f"✅ Chrome launched successfully (PID: {proc.pid})")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Chrome Launcher on CDP Port 9222")
    parser.add_argument("--platform", default="authors_republic", choices=list(PLATFORM_URLS.keys()), help="Target platform identifier")
    parser.add_argument("--url", default=None, help="Custom target URL (overrides platform default)")
    parser.add_argument("--port", type=int, default=9222, help="Remote debugging port (default: 9222)")
    parser.add_argument("--profile-dir", default=DEFAULT_PROFILE_DIR, help="Chrome user data directory")
    args = parser.parse_args()

    launch_browser(platform=args.platform, target_url=args.url, port=args.port, profile_dir=args.profile_dir)
