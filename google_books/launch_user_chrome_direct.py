import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def launch_chrome_direct():
    with sync_playwright() as p:
        chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        context = p.chromium.launch_persistent_context(
            user_data_dir=r"C:\tmp\chrome_dev_user",
            executable_path=chrome_exe,
            headless=False,
            viewport={"width": 1360, "height": 900},
            args=["--remote-debugging-port=9222"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://play.google.com/books/publish/")
        print("✅ Launched regular Google Chrome on your screen on Port 9222!")
        
        while True:
            time.sleep(1)

if __name__ == "__main__":
    launch_chrome_direct()
