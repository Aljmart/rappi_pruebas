from pathlib import Path
from playwright.sync_api import Page
from datetime import datetime

SCREENSHOT_DIR = Path("output/screenshots")

def take_screenshot(page: Page, prefix: str):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = SCREENSHOT_DIR / f"{prefix}_{timestamp}.png"
    page.screenshot(path=str(filename), full_page=True)
    print(f"Screenshot guardado: {filename}")