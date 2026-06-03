import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

// Parse command line args
const args = process.argv.slice(2);
const appKey = args[0] || 'npc-aggregator';

const config = JSON.parse(fs.readFileSync('config.json', 'utf8'));
const appConfig = config.apps[appKey];

if (!appConfig) {
  console.error(`App configuration for "${appKey}" not found in config.json.`);
  process.exit(1);
}

async function record() {
  const outputDir = path.join(process.cwd(), 'output', appKey);
  fs.mkdirSync(outputDir, { recursive: true });

  console.log(`Starting screen recording for: ${appConfig.name}`);
  console.log(`Targeting URL: ${appConfig.url}`);

  const browser = await chromium.launch({
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 390, height: 844 }, // Mobile 9:16 vertical view for TikTok/Shorts
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
    recordVideo: {
      dir: outputDir,
      size: { width: 390, height: 844 },
    }
  });

  const page = await context.newPage();

  // Run the sequence of actions from config
  for (const step of appConfig.video_flow) {
    console.log(`Executing: ${step.action} -> ${step.value || step.selector}`);
    
    try {
      if (step.action === 'navigate') {
        await page.goto(step.value);
      } else if (step.action === 'wait') {
        await page.waitForTimeout(step.value);
      } else if (step.action === 'click') {
        await page.click(step.selector);
        
        // Handle potential transient Synthesis Engine Failures on the estimate action
        if (step.selector && step.selector.includes('Estimate & Compare Net Price')) {
          let success = false;
          for (let attempt = 1; attempt <= 10; attempt++) {
            await page.waitForTimeout(3000);
            const content = await page.content();
            if (content.includes("Synthesis Engine Failed")) {
              console.log(`Synthesis failed (attempt ${attempt}). Retrying...`);
              await page.click("text=Go back and inspect your setup");
              await page.waitForTimeout(1000);
              await page.click(step.selector);
            } else if (content.includes("Personalized Comparisons") && !content.includes("Synthesis Engine Failed")) {
              console.log(`Results loaded successfully on attempt ${attempt}.`);
              success = true;
              break;
            }
          }
          if (!success) {
            console.error("Failed to load results after 10 attempts.");
          }
        }
      } else if (step.action === 'type') {
        await page.fill(step.selector, step.value);
      } else if (step.action === 'upload') {
        const fileInput = await page.locator(step.selector);
        await fileInput.setInputFiles(step.value);
      } else if (step.action === 'scroll') {
        if (step.value === 'bottom') {
          console.log("Scrolling to bottom of the page...");
          await page.evaluate(() => {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
          });
        } else {
          await page.locator(step.selector).scrollIntoViewIfNeeded();
        }
      }
    } catch (err) {
      console.error(`Step failed: ${step.action}. Error: ${err.message}`);
    }
  }

  // Close context to finish recording and save the video file
  await context.close();
  await browser.close();

  // Locate the generated video and rename it to a standard 'raw_recording.webm'
  const files = fs.readdirSync(outputDir);
  const videoFile = files.find(f => f.endsWith('.webm'));
  if (videoFile) {
    const oldPath = path.join(outputDir, videoFile);
    const newPath = path.join(outputDir, 'raw_recording.webm');
    if (fs.existsSync(newPath)) {
      fs.unlinkSync(newPath);
    }
    fs.renameSync(oldPath, newPath);
    console.log(`Recording saved successfully to: ${newPath}`);
  } else {
    console.error('No video recording file was found.');
  }
}

record().catch(console.error);
