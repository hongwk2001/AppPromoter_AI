import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const appKey = process.argv[2] || 'golf-swing-ai';
const sessionPath = path.join(process.cwd(), 'tiktok_session.json');

let videoPath;
let caption = "Check out our new local Reddit Replier tool! #developer #devlog #localLLM #ollama #gemma2 #tkinter #buildinpublic";

if (appKey === 'devlog') {
  videoPath = path.join(process.cwd(), 'output', 'kb_html', 'reddit_replier_launch.mp4');
} else {
  const outputDir = path.join(process.cwd(), 'output', appKey);
  videoPath = path.join(outputDir, 'final_shorts.mp4');
  const assetsPath = path.join(outputDir, 'marketing_assets.json');
  if (fs.existsSync(assetsPath)) {
    try {
      const assets = JSON.parse(fs.readFileSync(assetsPath, 'utf8'));
      caption = assets.linkedin_post || caption;
      caption = caption.replace(/#+\s+.*\n/g, '').trim();
      if (caption.length > 150) {
        caption = caption.slice(0, 140) + "... #Shorts #AppDemo #AI";
      }
    } catch (e) {
      console.warn("Could not read marketing_assets.json for caption, using default.");
    }
  }
}

if (!fs.existsSync(videoPath)) {
  console.error(`Error: Video file not found at ${videoPath}`);
  process.exit(1);
}

async function publish() {
  console.log(`Starting TikTok publishing flow for: ${appKey}`);

  const browser = await chromium.launch({
    headless: false, // Run headed so you can complete login, Captchas, and 2FA
    channel: 'chrome', // Use system Google Chrome to bypass Google login restrictions
    ignoreDefaultArgs: ['--enable-automation'], // Disable the 'controlled by automated software' bar
  });

  let context;
  const hasSession = fs.existsSync(sessionPath);
  
  if (hasSession) {
    console.log("Found existing TikTok session. Loading session state...");
    context = await browser.newContext({
      storageState: sessionPath,
      viewport: { width: 1280, height: 800 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
  } else {
    console.log("No existing session found. Starting fresh session...");
    context = await browser.newContext({
      viewport: { width: 1280, height: 800 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
  }

  const page = await context.newPage();

  // Stealth: Hide the webdriver property so Google allows signing in
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined,
    });
  });

  console.log("Navigating to TikTok upload page...");
  await page.goto("https://www.tiktok.com/tiktokstudio/upload");

  // Check if we are on the login page or upload page
  try {
    console.log("Checking login status (waiting up to 3 minutes for you to complete login / 2FA / Captchas)...");
    
    // We wait for the file input to appear on the page which confirms we are logged in and on the upload form
    await page.waitForSelector('input[type="file"]', { timeout: 180000 });
    
    console.log("Logged in state detected!");
    
    // Save session state so we don't need to log in next time
    const sessionState = await context.storageState();
    fs.writeFileSync(sessionPath, JSON.stringify(sessionState, null, 2));
    console.log(`Saved session state to: ${sessionPath}`);
    
  } catch (err) {
    console.error("Timeout or login failed. Please ensure you logged in successfully: " + err.message);
    await browser.close();
    process.exit(1);
  }

  // Upload video file
  console.log("Selecting video file for upload...");
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(videoPath);
  await page.waitForTimeout(5000);

  console.log("Waiting for video to process/upload...");
  await page.waitForTimeout(10000);

  // Write caption
  try {
    console.log("Entering caption...");
    // TikTok Studio upload uses a contenteditable div for the post description
    const editor = page.locator('div[contenteditable="true"]').or(page.locator('.public-DraftEditor-content'));
    await editor.first().click();
    
    // Clear default text if any by selecting all and backspacing
    await page.keyboard.press('Control+A');
    await page.keyboard.press('Backspace');
    await page.keyboard.insertText(caption);
    await page.waitForTimeout(2000);
  } catch (err) {
    console.warn("Could not fill caption automatically. You can enter it manually: " + err.message);
  }

  console.log("\n==============================================");
  console.log("ACTION REQUIRED:");
  console.log("Please review the post settings in the browser.");
  console.log("When ready, click 'Post' in the browser window to publish!");
  console.log("==============================================\n");

  // Keep browser open for 60 seconds so user can click Post
  await page.waitForTimeout(60000);
  
  await browser.close();
}

publish().catch(console.error);
