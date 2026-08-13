import { chromium } from 'playwright';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import readline from 'readline';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

(async () => {
    const authPath = path.join(__dirname, 'kdp_auth.json');
    if (!fs.existsSync(authPath)) {
        console.error('❌ Login state not found!');
        process.exit(1);
    }

    console.log('🚀 Starting KDP Field Inspector...');
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext({ storageState: authPath });
    const page = await context.newPage();

    await page.goto('https://kdp.amazon.com/en_US/bookshelf');

    console.log('\n======================================================');
    console.log('🛑 ACTION REQUIRED 🛑');
    console.log('Amazon KDP has 3 tabs: Details, Content, and Pricing.');
    console.log('We will scan each one. Click "+ Create new title" to start.');
    console.log('======================================================\n');
    
    const allFields = {};
    const tabs = ['Details', 'Content', 'Pricing'];

    for (const tab of tabs) {
        await new Promise((resolve) => rl.question(`\n👉 Go to the "${tab}" tab. Wait for it to load, then press [ENTER] to scan...\n`, resolve));

        console.log(`🔍 Scanning the ${tab} page...`);

        // Extract all input, textarea, and select fields
        const fieldsInfo = await page.evaluate(() => {
            const elements = Array.from(document.querySelectorAll('input, textarea, select'));
            return elements.map(el => {
                let labelText = '';
                if (el.id) {
                    const label = document.querySelector(`label[for="${el.id}"]`);
                    if (label) labelText = label.innerText.trim();
                }
                if (!labelText && el.closest('label')) {
                    labelText = el.closest('label').innerText.trim();
                }
                
                return {
                    tagName: el.tagName.toLowerCase(),
                    type: el.type || '',
                    id: el.id || '',
                    name: el.name || '',
                    placeholder: el.placeholder || '',
                    ariaLabel: el.getAttribute('aria-label') || '',
                    labelText: labelText
                };
            }).filter(f => f.type !== 'hidden'); // Ignore hidden fields
        });
        
        allFields[tab] = fieldsInfo;
        console.log(`✅ Extracted ${fieldsInfo.length} fields from ${tab}.`);
    }

    const outputPath = path.join(__dirname, 'kdp_fields.json');
    fs.writeFileSync(outputPath, JSON.stringify(allFields, null, 2));

    console.log(`\n🎉 Successfully extracted fields across all 3 tabs!`);
    console.log(`Saved to: ${outputPath}`);

    rl.close();
    await browser.close();
})();
