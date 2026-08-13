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
    const dataPath = path.join(__dirname, 'kdp_data.json');

    // 1. Check if auth file exists
    if (!fs.existsSync(authPath)) {
        console.error('❌ Login state not found!');
        console.error('Please run `node kdp_login.js` first to log in and save your session.');
        process.exit(1);
    }

    // 2. Load the book data
    const booksData = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
    const book = booksData[0]; // For now, just process the first book

    console.log(`🚀 Starting automated upload for: "${book.title}"`);

    // 3. Launch browser using the saved state
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext({ storageState: authPath });
    const page = await context.newPage();

    console.log('Navigating to Amazon KDP...');
    await page.goto('https://kdp.amazon.com/en_US/bookshelf');

    // Helper to try filling a field with multiple selectors
    const tryFill = async (selectors, value, fieldName) => {
        for (const selector of selectors) {
            try {
                const locator = page.locator(selector).first();
                if (await locator.isVisible({ timeout: 2000 })) {
                    await locator.fill(value);
                    console.log(`✅ Filled ${fieldName}`);
                    return;
                }
            } catch (e) {
                // Ignore and try next
            }
        }
        console.log(`⚠️ Could not automatically fill ${fieldName}`);
    };

    // Helper to prompt user
    const promptAndWait = (question) => {
        return new Promise((resolve) => rl.question(question, resolve));
    };

    // --- PHASE 2: DETAILS TAB ---
    console.log('\n======================================================');
    console.log('🛑 ACTION REQUIRED (DETAILS TAB) 🛑');
    console.log('Please click "+ Create new title" (or Kindle eBook) in the browser.');
    console.log('Once you are on the "Kindle eBook Details" page, come back here.');
    console.log('======================================================\n');
    
    await promptAndWait('\n👉 Press [ENTER] when you are on the Details page and ready to autofill...\n');

    let detailsAction = 'retry';
    while (detailsAction.toLowerCase() === 'retry') {
        console.log('\n🤖 Starting Details autofill sequence...');

        // 5. Autofill the data using exact IDs extracted from KDP
        await tryFill(['#data-title'], book.title, "Title");
        await tryFill(['#data-subtitle'], book.subtitle, "Subtitle");
        
        // Author names
        await tryFill(['#data-primary-author-first-name'], book.author_first_name, "Author First Name");
        await tryFill(['#data-primary-author-last-name'], book.author_last_name, "Author Last Name");

        // Contributors
        if (book.contributors && book.contributors.length > 0) {
            console.log('Filling Contributors...');
            for (let i = 0; i < book.contributors.length; i++) {
                const contributor = book.contributors[i];
                try {
                    const roleSelect = page.locator(`#data-contributors-${i}-role-native`).first();
                    if (await roleSelect.isVisible({ timeout: 2000 })) {
                        await roleSelect.selectOption({ label: contributor.role.charAt(0).toUpperCase() + contributor.role.slice(1) }).catch(() => {});
                    }
                } catch (e) {
                    console.log(`⚠️ Could not select role for contributor ${i}`);
                }
                await tryFill([`#data-contributors-${i}-first-name`], contributor.first_name, `Contributor ${i} First Name`);
                await tryFill([`#data-contributors-${i}-last-name`], contributor.last_name, `Contributor ${i} Last Name`);
            }
        }

        // Copyright
        try {
            const copyrightRadio = page.locator('#non-public-domain');
            if (await copyrightRadio.isVisible({ timeout: 2000 })) {
                await copyrightRadio.check();
                console.log('✅ Selected "I own the copyright"');
            }
        } catch (e) {
            console.log('⚠️ Could not automatically check copyright');
        }

        // Keywords
        console.log('Filling Keywords...');
        for (let i = 0; i < Math.min(book.keywords.length, 7); i++) {
            const keyword = book.keywords[i];
            await tryFill([`#data-keywords-${i}`], keyword, `Keyword ${i+1}`);
        }

        // Description
        console.log('Attempting to fill Description...');
        if (book.description) {
            try {
                const frame = page.frameLocator('iframe').first();
                const body = frame.locator('body');
                if (await body.isVisible({ timeout: 3000 })) {
                    await body.fill(book.description);
                    console.log('✅ Description filled in the rich text editor!');
                } else {
                    throw new Error("Iframe body not visible");
                }
            } catch (e) {
                console.log('⚠️ Could not automatically fill the Description. You may need to paste it manually.');
            }
        }

        console.log('\n🎉 Autofill attempt for Details tab complete!');
        detailsAction = await promptAndWait('👉 Review the fields. Type "retry" to try filling Details again, or press [ENTER] to move on...\n');
    }

    console.log('\nOnce you click "Save and Continue" manually, the script will naturally proceed to Phase 3 (Content)...');

    // --- PHASE 3: CONTENT TAB (UPLOADS) ---
    console.log('\n======================================================');
    console.log('🛑 ACTION REQUIRED (CONTENT TAB) 🛑');
    console.log('Please verify the Details tab, then click "Save and Continue".');
    console.log('Once you are on the "Kindle eBook Content" page, come back here.');
    console.log('======================================================\n');

    await promptAndWait('\n👉 Press [ENTER] when you are on the Content page and ready to upload files...\n');

    let contentAction = 'retry';
    while (contentAction.toLowerCase() === 'retry') {
        console.log('\n🤖 Starting file uploads...');

        // Upload Manuscript
        if (book.manuscript_path && fs.existsSync(book.manuscript_path)) {
            console.log('Uploading manuscript...');
            try {
                await page.locator('#data-assets-interior-file-upload-AjaxInput').setInputFiles(book.manuscript_path);
                console.log('✅ Manuscript upload initiated (Please wait for Amazon to process it on screen)');
            } catch (e) {
                console.log('⚠️ Failed to target manuscript upload button.');
            }
        } else {
            console.log('⚠️ Manuscript file not found or not specified.');
        }

        // Upload Cover
        if (book.cover_path && fs.existsSync(book.cover_path)) {
            console.log('Uploading cover image...');
            try {
                await page.locator('#data-assets-cover-file-upload-AjaxInput').setInputFiles(book.cover_path);
                console.log('✅ Cover upload initiated (Please wait for Amazon to process it on screen)');
            } catch (e) {
                console.log('⚠️ Failed to target cover upload button.');
            }
        } else {
            console.log('⚠️ Cover file not found or not specified.');
        }

        // AI-Generated Content Section
        if (book.ai_generated) {
            console.log('Filling AI-Generated Content section...');
            try {
                if (book.ai_generated.used) {
                    // Click the "Yes" radio button (assuming it's near the AI question)
                    const aiQuestion = page.locator('text="Did you use AI tools"');
                    if (await aiQuestion.isVisible({ timeout: 2000 })) {
                        await page.getByLabel('Yes', { exact: true }).first().check().catch(() => {});
                    }

                    // Texts
                    if (book.ai_generated.texts_level) {
                        await page.locator('#generative-ai-questionnaire-text').selectOption({ label: book.ai_generated.texts_level }).catch(() => {});
                        // Try to find the input next to it. It's usually the first textbox in the texts block.
                        const textBlock = page.locator('#generative-ai-questionnaire-text').locator('..').locator('..').locator('..');
                        await textBlock.locator('input[type="text"]').first().fill(book.ai_generated.texts_tools).catch(() => {});
                    }

                    // Images
                    if (book.ai_generated.images_level) {
                        await page.locator('#generative-ai-questionnaire-images').selectOption({ label: book.ai_generated.images_level }).catch(() => {});
                        const imgBlock = page.locator('#generative-ai-questionnaire-images').locator('..').locator('..').locator('..');
                        await imgBlock.locator('input[type="text"]').first().fill(book.ai_generated.images_tools).catch(() => {});
                    }

                    // Translations
                    if (book.ai_generated.translations_level) {
                        await page.locator('#generative-ai-questionnaire-translations').selectOption({ label: book.ai_generated.translations_level }).catch(() => {});
                        const transBlock = page.locator('#generative-ai-questionnaire-translations').locator('..').locator('..').locator('..');
                        await transBlock.locator('input[type="text"]').first().fill(book.ai_generated.translations_tools).catch(() => {});
                    }
                    console.log('✅ AI section filled!');
                } else {
                    await page.getByLabel('No', { exact: true }).first().check().catch(() => {});
                }
            } catch (e) {
                console.log('⚠️ Could not automatically fill AI section.');
            }
        }

        console.log('\n🎉 Upload attempt for Content tab complete!');
        contentAction = await promptAndWait('👉 Review the uploads. Type "retry" to attempt uploading again, or press [ENTER] to move on...\n');
    }

    // --- PHASE 4: PRICING TAB ---
    console.log('\n======================================================');
    console.log('🛑 ACTION REQUIRED (PRICING TAB) 🛑');
    console.log('Please wait for files to process, click "Save and Continue", and go to Pricing.');
    console.log('======================================================\n');
    
    await promptAndWait('\n👉 Press [ENTER] when you are on the Pricing page...\n');
    
    let pricingAction = 'retry';
    while (pricingAction.toLowerCase() === 'retry') {
        console.log('\n🤖 Starting Pricing autofill sequence...');
        
        // Just setting the price if available
        if (book.price) {
            await tryFill(['input[name*="price"]', 'input[id*="price"]'], book.price.toString(), "Price");
        }
        
        console.log('\n🎉 Pricing attempt complete!');
        pricingAction = await promptAndWait('👉 Review the Pricing tab. Type "retry" to attempt filling again, or press [ENTER] to finish...\n');
    }

    console.log('\n🎉 Automation completely finished!');
    console.log('You can now review everything and click Publish! The browser will stay open.');
    
    // Keep the browser open
    await new Promise(() => {}); // Wait forever so the browser doesn't close
})();
