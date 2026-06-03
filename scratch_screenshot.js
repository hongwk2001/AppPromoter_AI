import { chromium } from 'playwright';

async function checkSubmitButton() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();
  
  await page.goto("https://www.instagram.com/accounts/login/");
  await page.waitForTimeout(4000);
  
  const loginBtn = page.locator('text="Log in"').or(page.locator('a:has-text("Log in")'));
  await loginBtn.first().click();
  await page.waitForTimeout(4000);
  
  // Find all buttons or clickables on the actual login form
  const buttons = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('button, [role="button"], input[type="submit"]'))
      .map(el => ({
        tagName: el.tagName,
        text: el.innerText || el.textContent,
        type: el.type,
        className: el.className,
        html: el.outerHTML.slice(0, 150)
      }));
  });
  
  console.log("Buttons on the form page:");
  console.log(JSON.stringify(buttons, null, 2));
  
  await browser.close();
}

checkSubmitButton().catch(console.error);
