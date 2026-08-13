import os
import sys
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def launch_edge():
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_path):
        edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

    url = "https://play.google.com/books/publish/"
    user_data = r"C:\tmp\edge_dev_user"
    cmd = [edge_path, "--remote-debugging-port=9222", f"--user-data-dir={user_data}", url]
    
    print(f"🚀 Launching Edge browser on port 9222...")
    subprocess.Popen(cmd, creationflags=0x00000010)
    print("✅ Opened Edge browser window on your screen!")

if __name__ == "__main__":
    launch_edge()
