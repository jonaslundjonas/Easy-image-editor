from playwright.sync_api import sync_playwright, expect
import time
import os

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    filepath = os.path.abspath("index.html")
    page.goto(f"file://{filepath}")
    time.sleep(1)

    # Test Additive Selection (Rect)
    print("Testing Additive Selection (Rect)...")

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
    page.screenshot(path="/home/jules/verification/rect_additive_fail.png")

    # Test Deselect (Ctrl+D if implemented, otherwise menu)
    print("Testing Deselect...")
    page.evaluate("App.Tools.clearSelection()")
    time.sleep(0.2)

    # Test Additive Selection (Wand)
    print("Testing Additive Selection (Wand)...")

    # Draw Rect 1 (Red)
    page.evaluate("App.State.toolSettings.drawColor = '#ff0000'")
    page.click('button[data-tool="rect"]') # Corrected selector
    page.mouse.move(100, 300)
    page.mouse.down()
    page.mouse.move(150, 350)
    page.mouse.up()

    # Draw Rect 2 (Red)
    page.mouse.move(200, 300)
    page.mouse.down()
    page.mouse.move(250, 350)
    page.mouse.up()

    # Wand Select Rect 1
    page.click('button[data-tool="sel-wand"]')
    page.mouse.click(125, 325)

    # Shift + Wand Select Rect 2
    page.keyboard.down("Shift")
    page.mouse.click(225, 325)
    page.keyboard.up("Shift")

    time.sleep(0.5)
    page.screenshot(path="/home/jules/verification/wand_additive_fail.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
