from playwright.sync_api import sync_playwright, expect
import time
import os

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    filepath = os.path.abspath("index.html")
    page.goto(f"file://{filepath}")
    time.sleep(1)

    # 1. Test Global Color & Bucket
    # Select Bucket
    page.click('button[data-tool="bucket"]')
    # Set Global Color to Red
    page.fill('#global-color', '#ff0000')
    page.evaluate("App.State.toolSettings.drawColor = '#ff0000'") # Trigger logic if needed, but event listener should handle

    # Fill Canvas (Background is Transparent)
    # But wait, createNewProject makes it White or Black if selected.
    # Default is Transparent.
    # Bucket on transparent?
    # Tolerance 30.
    # Click 400, 300.
    page.mouse.click(400, 300)
    time.sleep(0.5)
    page.screenshot(path="./verification/1_bucket_fill.png")

    # 2. Test Duplicate Layer
    # Current layer is Red.
    # Click Duplicate.
    page.click('button[title="Duplicate Layer"]')
    time.sleep(0.2)
    # Check if new layer exists.
    # Layer name should be "Background copy" (if original was Background)
    # Or "Layer 1 copy".
    # Check text in layers-container.
    # content = page.inner_text('#layers-container')
    # print("Layers:", content)
    page.screenshot(path="./verification/2_duplicate_layer.png")

    # 3. Test Select All (Ctrl+A)
    page.keyboard.press("Control+A")
    time.sleep(0.5)
    # Should see outline around entire canvas (800x600).
    page.screenshot(path="./verification/3_select_all.png")

    # 4. Test Additive Selection (Shift)
    # Clear Selection
    page.evaluate("App.Tools.clearSelection()")

    # Select Rect 1
    page.click('button[data-tool="sel-rect"]')
    page.mouse.move(100, 100)
    page.mouse.down()
    page.mouse.move(200, 200)
    page.mouse.up()

    # Add Rect 2 (Shift)
    page.keyboard.down("Shift")
    page.mouse.move(300, 100)
    page.mouse.down()
    page.mouse.move(400, 200)
    page.mouse.up()
    page.keyboard.up("Shift")

    time.sleep(0.5)
    page.screenshot(path="./verification/4_additive_select.png")

    # 5. Test Transform Pivot & Aspect Ratio
    # Select Move Tool
    page.click('button[data-tool="move"]')
    # Start Transform
    page.evaluate("App.UI.startTransform()")
    time.sleep(0.2)
    page.screenshot(path="./verification/5_transform_start.png")

    # Drag TL handle. Pivot is BR.
    # TL handle is at x,y.
    # Center is 400, 300. Width 800, Height 600.
    # TL is at 0, 0.
    # BR is at 800, 600.
    # Drag TL to 100, 100.
    # New Width should be 700? (800 - 100)
    # New Height should be 500? (600 - 100)
    # Pivot (800, 600) should stay fixed.

    # We need to find where the handle is visually.
    # Handles are drawn on overlay canvas.
    # We'll just simulate drag.
    page.mouse.move(0 + 10, 0 + 50 + 35) # Offset for header/sidebar...
    # Wait, simple coordinates are relative to viewport.
    # Canvas area grid-area: canvas.
    # It's centered.
    # Let's use `page.evaluate` to get canvas rect.

    canvas_box = page.locator('#main-canvas').bounding_box()
    # TL corner is at canvas_box.x, canvas_box.y.

    page.mouse.move(canvas_box['x'], canvas_box['y']) # TL
    page.mouse.down()
    # Drag inward + Shift
    page.keyboard.down("Shift")
    page.mouse.move(canvas_box['x'] + 100, canvas_box['y'] + 100)
    page.mouse.up()
    page.keyboard.up("Shift")

    time.sleep(0.5)
    page.screenshot(path="./verification/6_transform_shift.png")

    # Apply
    page.click('button[onclick="App.UI.applyTransform()"]')

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
