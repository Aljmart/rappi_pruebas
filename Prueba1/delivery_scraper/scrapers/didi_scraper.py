from typing import List, Optional
from datetime import datetime
from playwright.sync_api import Page
from models.record import ScrapeRecord
from .base_scraper import BaseScraper
from utils.screenshots import take_screenshot
import unicodedata
import re
def normalize(text: str):
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9 +]", "", text)
    return text.strip()
class DidiScraper(BaseScraper):

    def __init__(self, page: Page):
        self.page = page
        self.platform_name = "didi"


    def set_address(self, address_text: str):
        self.page.goto("https://www.didi-food.com/es-MX", wait_until="domcontentloaded")
        take_screenshot(self.page, "didi_home")

        # Selector correcto y robusto
        address_input = self.page.locator("input[placeholder*='dirección']")
        address_input.wait_for(timeout=15000)
        address_input.fill(address_text)
        take_screenshot(self.page, "didi_address_filled")

        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(5000)
        take_screenshot(self.page, "didi_restaurants_loaded")


    def find_restaurant(self, keyword: str):
        cards = self.page.locator("[data-testid='store-card']").all()

        for c in cards:
            try:
                name = c.locator("[data-testid='store-name']").inner_text().lower()
                if keyword in name:
                    return c
            except:
                continue

        return None


    def open_restaurant(self, card):
        card.click()
        self.page.wait_for_timeout(4000)
        take_screenshot(self.page, "didi_restaurant_opened")


    def get_menu_items(self):
        take_screenshot(self.page, "didi_menu_loaded")

        items = self.page.locator("[data-testid='product-card']").all()
        results = []

        for item in items:
            try:
                name = item.locator("[data-testid='product-name']").inner_text()
            except:
                continue

            try:
                price_raw = item.locator("[data-testid='product-price']").inner_text()
                price = float(price_raw.replace("$", "").replace(",", "").strip())
            except:
                price = None

            results.append({
                "card": item,
                "name": name,
                "price": price
            })

        return results

    def open_product(self, item_card):
        item_card.click()
        self.page.wait_for_timeout(2000)
        take_screenshot(self.page, "didi_product_opened")


    def extract_product_modal(self):

        options = self.page.locator("[data-testid='option-item']").all()
        for opt in options:
            try:
                opt.click()
                self.page.wait_for_timeout(300)
            except:
                pass

        take_screenshot(self.page, "didi_product_customized")


        try:
            final_raw = self.page.locator("[data-testid='product-total-price']").inner_text()
            final_price = float(final_raw.replace("$", "").replace(",", "").strip())
        except:
            final_price = None


        try:
            self.page.locator("[data-testid='close-button']").click()
        except:
            self.page.keyboard.press("Escape")

        return final_price


    def scrape_address(self, addr_id: str, addr_text: str) -> List[ScrapeRecord]:

        self.set_address(addr_text)


        restaurant_card = self.find_restaurant("mcdonald")
        if not restaurant_card:
            print(f"[DiDi] No se encontró McDonald's en {addr_id}")
            return []

        self.open_restaurant(restaurant_card)

        menu_items = self.get_menu_items()

        records = []

        for item in menu_items:

            if "big mac" not in item["name"].lower():
                continue

            self.open_product(item["card"])
            final_price = self.extract_product_modal()

            record = ScrapeRecord(
                platform="didi",
                address_id=addr_id,
                address_text=addr_text,
                restaurant_name="McDonald's",
                restaurant_id="didi-no-id",
                category="Big Mac",
                item_name=item["name"],
                item_description="",
                final_price=final_price,
                original_price=item["price"],
                discount=None,
                delivery_time=None,
                delivery_fee=None,
                distance_km=None,
                timestamp=datetime.now().isoformat()
            )

            records.append(record)

        return records
