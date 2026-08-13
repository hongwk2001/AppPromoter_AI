@echo off
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 1 /nobreak >nul
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\tmp\chrome_dev_user" "https://play.google.com/books/publish/"
