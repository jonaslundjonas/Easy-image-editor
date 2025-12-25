
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Load the local index.html
        import os
        cwd = os.getcwd()
        await page.goto(f"file://{cwd}/index.html")

        # Wait for app to load
        await page.wait_for_selector("#main-canvas")

        # --- Test 1: Brush Hardness 100% ---
        # Select Paint Brush
        await page.click("button[data-tool='paint']")
        # Set Color to Red
        await page.fill("#global-color", "#ff0000")
        await page.evaluate("App.State.toolSettings.drawColor = '#ff0000'")
        # Set Size to 30
        await page.evaluate("App.State.toolSettings.brushSize = 30")
        # Set Hardness to 100%
        await page.evaluate("App.State.toolSettings.brushHardness = 100")

        # Draw a line
        canvas = page.locator("#canvas-area")
        box = await canvas.bounding_box()

        start_x = box["x"] + 100
        start_y = box["y"] + 100

        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        await page.mouse.move(start_x + 100, start_y + 100)
        await page.mouse.up()

        # Screenshot
        await page.screenshot(path="brush_100_hardness.png")
        print("--- Test 1: Brush Hardness 100% ---")
        print("Brush test done.")

        # --- Test 2: Smudge Tool ---
        # Select Smudge Tool
        await page.click("button[data-tool='smudge']")
        # Set Size to 50
        await page.evaluate("App.State.toolSettings.brushSize = 50")

        # Drag from the red line downwards into the black area
        # The red line ended at (start_x + 100, start_y + 100)
        smudge_start_x = start_x + 100
        smudge_start_y = start_y + 100

        await page.mouse.move(smudge_start_x, smudge_start_y)
        await page.mouse.down()
        # Drag down by 100px
        await page.mouse.move(smudge_start_x, smudge_start_y + 100, steps=10)
        await page.mouse.up()

        await page.screenshot(path="smudge_result.png")
        print("--- Test 2: Smudge Tool ---")
        print("Smudge test done.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
