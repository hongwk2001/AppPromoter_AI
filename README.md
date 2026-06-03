# AppPromoter AI 🚀

AppPromoter AI is a reusable marketing and launching engine that automatically generates copywriting, records vertical TikTok/Short demo videos of your app in action, synthesizes AI voice narration, and automates outreach.

## 📁 Repository Structure

*   `config.json`: Project configuration file storing details for the apps you want to promote (e.g. Golf Swing AI, NPC Aggregator).
*   `requirements.txt`: Python package dependencies (Gemini API, moviepy, etc.).
*   `package.json`: Node dependencies for running browser automation.
*   `recorder.js`: Playwright script that interacts with the app UI and records vertical viewports.
*   `copywriter.py`: Gemini-powered script that generates launch threads, LinkedIn articles, emails, and TTS voiceover scripts.
*   `stitcher.py`: Python module using FFmpeg to merge the UI recordings and the voiceover audio into subtitled `9:16` videos.
*   `outreach.py`: Automation script to send bulk personalized email outreach to a CSV contact sheet.

## 🚀 Getting Started

1. Install Node dependencies:
   ```bash
   npm install
   npx playwright install chromium
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your API keys (`GEMINI_API_KEY`, etc.) to a `.env` file.
4. Customize `config.json` for your target application.
5. Run the automation pipeline:
   ```bash
   python main.py --app golf-swing-ai --actions record,write,stitch
   ```
