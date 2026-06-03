import { chromium } from 'playwright';

async function testComplete() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  console.log("Navigating to app...");
  await page.goto("https://swingpro-ai-206752517500.us-west2.run.app/");
  await page.waitForTimeout(3000);
  
  console.log("Locating file input...");
  const fileInput = await page.locator('input[type="file"]');
  
  console.log("Uploading file...");
  await fileInput.setInputFiles('D:\\git_repo\\golfswingai\\images\\extracted_video.mp4');
  
  // Wait for 20 seconds and check DOM
  for (let i = 1; i <= 4; i++) {
    await page.waitForTimeout(5000);
    console.log(`\n--- DOM after ${i * 5}s ---`);
    const text = await page.evaluate(() => document.body.innerText);
    console.log(text.split('\n').filter(line => line.trim().length > 0).slice(0, 30).join('\n'));
  }

  await browser.close();
}

testComplete().catch(console.error);
