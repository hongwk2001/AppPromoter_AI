import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

// Parse .env file natively
const env = {};
if (fs.existsSync('.env')) {
  const envContent = fs.readFileSync('.env', 'utf8');
  envContent.split('\n').forEach(line => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#')) {
      const [key, ...parts] = trimmed.split('=');
      if (key) {
        env[key.trim()] = parts.join('=').trim();
      }
    }
  });
}

const appKey = process.argv[2] || 'golf-swing-ai';
const outputDir = path.join(process.cwd(), 'output', appKey);
const videoPath = path.join(outputDir, 'final_shorts.mp4');
const assetsPath = path.join(outputDir, 'marketing_assets.json');

const username = env.INSTAGRAM_USERNAME || process.env.INSTAGRAM_USERNAME;
const password = env.INSTAGRAM_PASSWORD || process.env.INSTAGRAM_PASSWORD;

if (!username || !password) {
  console.error("Error: INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD must be defined in your .env file.");
  process.exit(1);
}

if (!fs.existsSync(videoPath)) {
  console.error(`Error: Video file not found at ${videoPath}`);
  process.exit(1);
}

async function publish() {
  console.log(`Starting Instagram publishing flow for: ${appKey}`);
  
  // Read caption from marketing assets
  let caption = "Check out SwingPro AI!";
  if (fs.existsSync(assetsPath)) {
    try {
      const assets = JSON.parse(fs.readFileSync(assetsPath, 'utf8'));
      // Use the LinkedIn post copy or a summary for Instagram
      caption = assets.linkedin_post || caption;
      // Strip markdown headers if present
      caption = caption.replace(/#+\s+.*\n/g, '').trim();
    } catch (e) {
      console.warn("Could not read marketing_assets.json for caption, using default.");
    }
  }

  const sessionPath = path.join(process.cwd(), 'instagram_session.json');
  const browser = await chromium.launch({
    headless: false, // Run headed so you can complete any 2FA/verification prompts
    channel: 'chrome', // Use system Google Chrome to bypass Google login restrictions
    ignoreDefaultArgs: ['--enable-automation'], // Disable the 'controlled by automated software' bar
  });

  let context;
  const hasSession = fs.existsSync(sessionPath);

  if (hasSession) {
    console.log("Found existing Instagram session. Loading session state...");
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

  if (hasSession) {
    console.log("Navigating to Instagram home...");
    await page.goto("https://www.instagram.com/");
    await page.waitForTimeout(5000);
  } else {
    console.log("Navigating to Instagram login...");
    await page.goto("https://www.instagram.com/accounts/login/");
    await page.waitForTimeout(5000);

    // Check if login inputs are immediately visible; if not, click the Log in link/button
    try {
      if (await page.locator('input[name="username"]').count() === 0) {
        console.log("Login inputs not immediately visible. Attempting to click 'Log in' link...");
        const loginBtn = page.locator('text="Log in"').or(page.locator('a:has-text("Log in")'));
        await loginBtn.first().click();
        await page.waitForTimeout(3000);
      }
    } catch (err) {
      console.log("Could not find or click Log in redirect link: " + err.message);
    }

    // Fill credentials
    console.log("Filling login credentials...");
    const usernameInput = page.locator('input[name="username"]').or(page.locator('input[name="email"]'));
    const passwordInput = page.locator('input[name="password"]').or(page.locator('input[name="pass"]'));
    await usernameInput.first().fill(username);
    await passwordInput.first().fill(password);
    
    console.log("Submitting login form...");
    await passwordInput.first().press('Enter');

    console.log("Waiting for user to be logged in (please enter your 2FA / verification code in the browser window)...");
    // We wait for the home feed or search icons to confirm login
    await page.waitForSelector('svg[aria-label="Home"]', { timeout: 180000 });
    console.log("Successfully logged in!");
    await page.waitForTimeout(5000);

    // Save session state
    const sessionState = await context.storageState();
    fs.writeFileSync(sessionPath, JSON.stringify(sessionState, null, 2));
    console.log(`Saved session state to: ${sessionPath}`);
  }

  // Dismiss "Save Info" if visible
  try {
    const saveInfoBtn = page.locator('text="Not Now"').or(page.locator('button:has-text("Not Now")'));
    if (await saveInfoBtn.count() > 0) {
      console.log("Dismissing Save Info prompt...");
      await saveInfoBtn.first().click();
      await page.waitForTimeout(3000);
    }
  } catch (err) {
    console.log("No Save Info prompt detected.");
  }

  // Dismiss "Turn on Notifications" if visible
  try {
    const notifsBtn = page.locator('button:has-text("Not Now")').or(page.locator('text="Not Now"'));
    if (await notifsBtn.count() > 0) {
      console.log("Dismissing Notifications prompt...");
      await notifsBtn.first().click();
      await page.waitForTimeout(3000);
    }
  } catch (err) {
    console.log("No Notifications prompt detected.");
  }

  // Locate and click "Create" button
  console.log("Opening new post creator...");
  try {
    const createBtn = page.locator('[aria-label="New post"]').or(page.locator('text="Create"'));
    await createBtn.first().click();
    await page.waitForTimeout(2000);

    // Instagram sub-menu: click "Post"
    console.log("Clicking 'Post' in the sub-menu...");
    const postBtn = page.locator('text="Post"').or(page.locator('span:has-text("Post")')).or(page.locator('svg[aria-label="Post"]'));
    await postBtn.first().click();
    await page.waitForTimeout(2000);
  } catch (err) {
    console.log("Could not click Create/Post buttons automatically. You may need to click them manually.");
  }

  console.log("\n==============================================");
  console.log("ACTION REQUIRED:");
  console.log("If the 'Create New Post' window is not open, please manually");
  console.log("click the '+' (Create) button in the Instagram sidebar.");
  console.log("==============================================\n");

  // Upload video file
  console.log("Waiting for file uploader to be visible (up to 2 minutes)...");
  const fileInput = page.locator('input[type="file"]');
  await fileInput.waitFor({ state: 'attached', timeout: 120000 });
  
  console.log("Selecting video file for upload...");
  await fileInput.setInputFiles(videoPath);
  await page.waitForTimeout(5000);

  // Handle video ratio/crop if needed, then click "Next"
  console.log("Clicking Next through Crop screen...");
  const nextBtn = page.locator('text="Next"').or(page.locator('div[role="button"]:has-text("Next")'));
  await nextBtn.first().click({ force: true });
  await page.waitForTimeout(3000);

  // Click Next on Edit screen
  console.log("Clicking Next through Edit screen...");
  await nextBtn.first().click({ force: true });
  await page.waitForTimeout(3000);

  // Fill caption
  console.log("Writing caption...");
  const captionArea = page.locator('[aria-label="Write a caption..."]');
  await captionArea.fill(caption);
  await page.waitForTimeout(2000);

  // Click Share
  console.log("Clicking Share to publish post...");
  const shareBtn = page.locator('text="Share"').or(page.locator('div[role="button"]:has-text("Share")'));
  await shareBtn.first().click({ force: true });

  console.log("Waiting for post completion...");
  // Wait up to 2 minutes for upload to finish and confirmation message
  await page.waitForSelector('text="Your post has been shared."', { timeout: 120000 });
  console.log("Post successfully shared to Instagram!");
  await page.waitForTimeout(5000);

  await browser.close();
}

publish().catch(console.error);
