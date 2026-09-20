"""
start_d2d_browser.py
Launches Google Chrome on CDP port 9222 for Draft2Digital.
Delegates to universal start_browser.py launcher.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from start_browser import launch_browser

if __name__ == "__main__":
    launch_browser(platform="draft2digital", profile_dir=r"C:\tmp\chrome_dev_user")
