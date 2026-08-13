import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';
import readline from 'readline';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

(async () => {
    console.log('🚀 Launching Playwright to capture Amazon KDP login state...');
    
    // Launch browser in headful mode so the user can interact
    const browser = await chromium.launch({ headless: false });
    
    // Create a new context
    const context = await browser.newContext();
    const page = await context.newPage();
    
    console.log('Navigating to Amazon KDP...');
    await page.goto('https://kdp.amazon.com/en_US/bookshelf');
    
    console.log('\n======================================================');
    console.log('🛑 ACTION REQUIRED 🛑');
    console.log('Please log into Amazon KDP in the browser window.');
    console.log('Solve any Captchas and enter your SMS 2FA code.');
    console.log('The script will wait until you reach the Bookshelf page.');
    console.log('======================================================\n');
    
    // Wait for the user to press Enter in the terminal
    await new Promise((resolve) => {
        rl.question('\n👉 Press [ENTER] here in the terminal AFTER you have successfully logged in and can see your Bookshelf...\n', () => {
            resolve();
        });
    });

    console.log('✅ Saving login state...');
    try {
        // Save the storage state (cookies, local storage)
        const authPath = path.join(__dirname, 'kdp_auth.json');
        await context.storageState({ path: authPath });
        
        console.log(`\n🎉 Login state saved successfully to ${authPath}`);
        console.log('You can now run the automated scripts without logging in again.');
        
    } catch (e) {
        console.error('❌ Failed to save login state:', e);
    }

    rl.close();
    await browser.close();
})();
