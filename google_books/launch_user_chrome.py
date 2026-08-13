import os
import sys
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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

def launch_chrome():
    chrome_path = find_chrome()
    if not chrome_path:
        print("❌ Could not find regular Google Chrome executable.")
        return

    url = "https://play.google.com/books/publish/"
    user_data = r"C:\tmp\chrome_dev_user"
    cmd = [chrome_path, f"--remote-debugging-port=9222", f"--user-data-dir={user_data}", url]
    
    print(f"🚀 Launching regular Google Chrome: {chrome_path}")
    subprocess.Popen(cmd, creationflags=0x00000010) # DETACHED_PROCESS / NEW_CONSOLE
    print("✅ Opened regular Google Chrome with port 9222 enabled!")

if __name__ == "__main__":
    launch_chrome()
