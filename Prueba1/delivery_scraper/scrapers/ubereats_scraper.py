from datetime import datetime
from playwright.sync_api import Page
from models.record import ScrapeRecord
from utils.screenshots import take_screenshot

import unicodedata
import re

TARGET_PRODUCTS = [
    "big mac tocino + favoritos"
]

TARGET_RESTAURANTS = [
    "mcdonald",

]


class UberEatsScraper:

    def __init__(self, page: Page):
        self.page = page
        self.platform_name = "ubereats"

    def close_cookies(self):
        try:
            btn = self.page.get_by_role("button", name="Aceptar")
            if btn.is_visible():
                btn.click()
                self.page.wait_for_timeout(1000)
        except:
            pass
    def normalize(self, text: str):
        text = text.lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))
        text = re.sub(r"[^a-z0-9 +]", "", text)
        text = text.replace("  ", " ").strip()
        return text

    def is_target_product(self, name: str):
        clean = self.normalize(name)
        return clean in TARGET_PRODUCTS

    def find_restaurant_by_name(self, keyword: str):
        cards = self.page.locator("a[href*='/store/']").all()

        for c in cards:
            try:
                name = c.locator("h3").inner_text(timeout=2000).lower()
                href = c.get_attribute("href")

                if href.startswith("/"):
                    href = "https://www.ubereats.com" + href

                if keyword in name:
                    return {
                        "name": name,
                        "id": href.split("/")[-1].split("?")[0],
                        "url": href
                    }
            except:
                continue

        return None

    def set_address(self, address_text: str):

        self.page.goto("https://www.ubereats.com/mx", wait_until="domcontentloaded")
        take_screenshot(self.page, "ubereats_home")

        self.page.evaluate("window.scrollTo(0, 0)")
        self.page.wait_for_timeout(500)
        self.page.evaluate("window.scrollBy(0, 200)")
        self.page.wait_for_timeout(500)

        visible_input = self.page.locator("input[placeholder='Ingresa la dirección de entrega']")

        try:
            visible_input.wait_for(timeout=20000)
        except:
            self.page.reload(wait_until="domcontentloaded")
            self.page.wait_for_timeout(2000)
            visible_input = self.page.locator("input[placeholder='Ingresa la dirección de entrega']")
            visible_input.wait_for(timeout=20000)

        visible_input.click(force=True)
        self.page.wait_for_timeout(800)

        for char in address_text:
            visible_input.type(char, delay=120)

        take_screenshot(self.page, "ubereats_address_filled")
        self.page.wait_for_timeout(2000)

        box = visible_input.bounding_box()
        self.page.mouse.click(
            box["x"] + box["width"] / 2,
            box["y"] + box["height"] + 30
        )

        self.page.wait_for_timeout(6000)
        take_screenshot(self.page, "ubereats_restaurants_loaded")


    def get_restaurants(self):
        cards = self.page.locator("a[href*='/store/']").all()

        restaurants = []
        for c in cards:
            try:
                name = c.locator("h3").inner_text(timeout=2000)
                href = c.get_attribute("href")
                restaurants.append({
                    "name": name,
                    "id": href.split("/")[-1].split("?")[0],
                    "url": href
                })
            except:
                continue

        return restaurants[:5]   # limitar para pruebas


    def open_restaurant(self, restaurant):
        self.page.goto(restaurant["url"], wait_until="domcontentloaded")
        self.page.wait_for_timeout(4000)
        take_screenshot(self.page, f"ubereats_restaurant_{restaurant['name']}")

    def get_menu_items(self):

        take_screenshot(self.page, "ubereats_menu_loaded")

        items = []


        last_height = 0
        for _ in range(10):
            self.page.mouse.wheel(0, 2000)
            self.page.wait_for_timeout(800)
            new_height = self.page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height


        cards = self.page.locator("li[data-testid^='store-item-']").all()

        if not cards:
            print("No se encontraron ítems con li[data-testid^='store-item-']")
            return items

        for card in cards:
            try:

                name = card.locator("span").first.inner_text(timeout=2000)
            except:
                continue


            try:
                price_raw = card.locator("span:has-text('$')").first.inner_text()
                price = float(price_raw.replace("$", "").replace(",", "").strip())
            except:
                price = None


            try:
                desc = card.locator("span").nth(1).inner_text()
            except:
                desc = ""

            items.append({
                "card": card,
                "name": name,
                "description": desc,
                "price": price
            })

        print(f" Se encontraron {len(items)} ítems en el menú")
        return items

    def extract_product_modal(self):


        options = self.page.locator("[data-testid='customization-option']").all()
        for opt in options:
            try:
                opt.click()
                self.page.wait_for_timeout(400)
            except:
                pass

        take_screenshot(self.page, "ubereats_product_customized")


        price_spans = self.page.locator("span[data-testid='rich-text']:has-text('$')")

        try:
            final_price_raw = price_spans.nth(0).inner_text()
            final_price = float(final_price_raw.replace("$", "").replace(",", "").strip())
        except:
            final_price = None

        try:
            original_price_raw = price_spans.nth(1).inner_text()
            original_price = float(original_price_raw.replace("$", "").replace(",", "").strip())
        except:
            original_price = None


        try:
            discount_raw = self.page.locator("div:has-text('%')").first.inner_text()
            discount = discount_raw.strip()
        except:
            discount = None


        try:
            self.page.locator("[data-testid='close-button']").click()
        except:
            try:
                self.page.keyboard.press("Escape")
            except:
                pass

        return {
            "final_price": final_price,
            "original_price": original_price,
            "discount": discount
        }

    def open_product(self, product_name):

        span = self.page.locator("span", has_text=product_name).first

        if not span or span.count() == 0:
            take_screenshot(self.page, "product_not_found_span")
            print("⚠ No se encontró el span del producto")
            return None

        link = span.locator("xpath=ancestor::a[1]").first

        if not link or link.count() == 0:
            take_screenshot(self.page, "product_no_link")
            print("⚠ No se encontró el enlace del producto")
            return None

        link.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)
        link.click(force=True)
        self.page.wait_for_timeout(2000)

        take_screenshot(self.page, "product_modal_opened")

        return self.extract_product_modal()

    def scrape_address(self, addr_id: str, addr_text: str):

        records = []

        self.set_address(addr_text)

        for target in TARGET_RESTAURANTS:

            restaurant = self.find_restaurant_by_name(target)

            if not restaurant:
                print(f"No se encontró {target} en {addr_id}")
                continue


            self.open_restaurant(restaurant)

            menu_items = self.get_menu_items()


            for item in menu_items:

                if "big mac tocino + favoritos" not in item["name"].lower():
                    continue

                final_price = self.open_product(item["name"])


                records.append(
                    ScrapeRecord(
                        platform="ubereats",
                        address_id=addr_id,
                        address_text=addr_text,
                        restaurant_name=restaurant["name"],
                        restaurant_id=restaurant["id"],
                        category="Big Mac Tocino + favoritos",
                        item_name=item["name"],
                        item_description=item["description"],
                        item_price=final_price["final_price"],
                        item_original_price=final_price["original_price"],
                        item_discount=final_price["discount"],

                        timestamp=datetime.now().isoformat()
                    )
                )

        return records

