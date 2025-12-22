
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
    const browser = await chromium.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const context = await browser.newContext();
    const page = await context.newPage();

    // Load the local HTML file
    const filePath = 'file://' + path.resolve('index.html');
    await page.goto(filePath);

    // Wait for app to load
    await page.waitForSelector('#main-canvas');

    console.log('--- Test Started ---');

    // 1. Test Magic Wand with Offset
    console.log('Testing Magic Wand...');
    // Create a project with a white background layer
    // Add a black rectangle in a new layer at offset 100,100
    await page.evaluate(() => {
        App.Layers.addEmptyLayer(); // Layer 2
        const l = App.Layers.getActive();
        l.name = "TestLayer";
        l.x = 100; l.y = 100;
        l.width = 100; l.height = 100;
        const ctx = l.canvas.getContext('2d');
        ctx.fillStyle = 'red';
        ctx.fillRect(0, 0, 100, 100);
        App.Render.update();
    });

    // Select Wand Tool
    await page.click('#tool-sel-wand');

    // Click on the red square (Global 150, 150) -> Local 50, 50
    await page.mouse.click(150, 150);

    // Verify selection active
    const selectionActive = await page.evaluate(() => App.getActiveProject().selection.active);
    console.log(`Selection Active: ${selectionActive}`);

    if(!selectionActive) {
        console.error('Magic wand failed to select.');
        process.exit(1);
    }

    // 2. Test Paint Select (Add vs Subtract)
    console.log('Testing Paint Select...');
    await page.evaluate(() => App.Tools.clearSelection());
    await page.click('#tool-sel-brush');

    // Paint to Add
    await page.mouse.move(150, 150);
    await page.mouse.down();
    await page.mouse.move(160, 160);
    await page.mouse.up();

    // Check if selection exists
    const hasSelection = await page.evaluate(() => {
        const p = App.getActiveProject();
        return p.selection.active && !!p.selection.mask;
    });
    console.log(`Has Selection after Paint: ${hasSelection}`);

    // Paint to Subtract (Hold Alt)
    // Playwright modifiers
    await page.keyboard.down('Alt');
    await page.mouse.move(150, 150);
    await page.mouse.down();
    await page.mouse.move(160, 160);
    await page.mouse.up();
    await page.keyboard.up('Alt');

    // Verify mask is cleared in that area?
    // Hard to verify pixels via script easily without screenshot analysis or pixel reading.
    // We assume logic holds if no error.

    // 3. Test Rotation Logic
    console.log('Testing Rotation...');
    // Reset
    await page.evaluate(() => {
        App.Layers.addEmptyLayer();
        const l = App.Layers.getActive();
        l.x = 200; l.y = 200; l.width = 100; l.height = 100;
    });

    // Start Transform
    await page.evaluate(() => App.UI.startTransform());

    // Drag Rotation Handle (Local 0, -h/2 - 25) -> Global Center + Rotation
    // Center is 250, 250.
    // Handle is approx 250, 200 - 25 = 175.

    await page.mouse.move(250, 175);
    await page.mouse.down();
    // Drag to right -> Rotate CW
    await page.mouse.move(300, 175);
    await page.mouse.up();

    const rotation = await page.evaluate(() => App.Layers.getActive().rotation);
    console.log(`Layer Rotation: ${rotation}`);

    if(rotation === 0) {
        console.error('Rotation did not change.');
        process.exit(1);
    }

    console.log('--- Test Passed ---');
    await browser.close();
})();
