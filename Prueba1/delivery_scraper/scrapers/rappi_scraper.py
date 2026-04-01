from typing import List, Optional
from datetime import datetime
from playwright.sync_api import Page
from models.record import ScrapeRecord
from .base_scraper import BaseScraper
from utils.screenshots import take_screenshot


def parse_price(text: str) -> Optional[float]:
    if not text:
        return None
    cleaned = text.replace("$", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except:
        return None


class RappiScraper(BaseScraper):

    def __init__(self, page: Page):
        self.page = page
        self.platform_name = "rappi"

    def set_address(self, address_text: str):
        self.page.goto("https://www.rappi.com.mx", wait_until="networkidle")
        take_screenshot(self.page, "rappi_home")


        address_input = self.page.locator(
            "input[placeholder='¿Dónde quieres recibir tu compra?']"
        )
        address_input.wait_for(timeout=20000)


        for ch in address_text:
            address_input.type(ch, delay=120)  # 120ms entre teclas
        take_screenshot(self.page, "rappi_address_typed")


        suggestions = self.page.locator("[data-testid='address-suggestion-item']")
        suggestions.first.wait_for(timeout=20000)
        take_screenshot(self.page, "rappi_suggestions_visible")


        suggestions.first.click()
        take_screenshot(self.page, "rappi_suggestion_selected")


        self.page.wait_for_timeout(5000)
        take_screenshot(self.page, "rappi_restaurants_loaded")


        self.page.wait_for_timeout(1500)

        suggestions = self.page.locator("[data-testid='address-suggestion-item']")
        suggestions.first.wait_for(timeout=20000)
        suggestions.first.click()
        take_screenshot(self.page, "rappi_suggestion_selected")


        self.page.wait_for_timeout(5000)
        take_screenshot(self.page, "rappi_restaurants_loaded")


    def open_restaurant(self, name_contains: str):
        restaurant = self.page.locator(
            f"div[data-testid='store-card'] >> text={name_contains}"
        )
        restaurant.first.click()
        self.page.wait_for_timeout(5000)
        take_screenshot(self.page, f"rappi_restaurant_{name_contains}")

    def scrape_address(self, address_id: str, address_text: str) -> List[ScrapeRecord]:

        self.set_address(address_text)

        records: List[ScrapeRecord] = []

        target_restaurant = "McDonald"
        self.open_restaurant(target_restaurant)

        restaurant_name = self.page.locator(
            "h1[data-testid='store-name']"
        ).first.inner_text()


        items = self.page.locator("div[data-testid='product-card']").all()
        take_screenshot(self.page, "rappi_menu_loaded")

        for item in items[:10]:


            item_name = item.locator("h3, h4, span").first.inner_text()


            price_text = ""
            if item.locator("span[data-testid='product-price']").count() > 0:
                price_text = item.locator(
                    "span[data-testid='product-price']"
                ).first.inner_text()

            original_price = parse_price(price_text)


            add_button = item.locator("button[data-testid='add-product']")
            if add_button.count() == 0:
                continue

            add_button.first.click()
            self.page.wait_for_timeout(2000)
            take_screenshot(self.page, f"rappi_item_added_{item_name}")


            self.page.locator(
                "a:has-text('Ver carrito'), button:has-text('Ver carrito')"
            ).first.click()
            self.page.wait_for_timeout(4000)
            take_screenshot(self.page, f"rappi_cart_{item_name}")


            delivery_fee = None
            if self.page.locator("div:has-text('Costo de envío') span").count() > 0:
                delivery_fee = parse_price(
                    self.page.locator(
                        "div:has-text('Costo de envío') span"
                    ).last.inner_text()
                )

            service_fee = None
            if self.page.locator("div:has-text('Tarifa de servicio') span").count() > 0:
                service_fee = parse_price(
                    self.page.locator(
                        "div:has-text('Tarifa de servicio') span"
                    ).last.inner_text()
                )


            final_price = None
            if self.page.locator("div:has-text('Total') span").count() > 0:
                final_price = parse_price(
                    self.page.locator("div:has-text('Total') span").last.inner_text()
                )


            eta_min, eta_max = None, None
            if self.page.locator("span:has-text('min')").count() > 0:
                eta_text = self.page.locator("span:has-text('min')").first.inner_text()
                if "–" in eta_text:
                    parts = eta_text.split("–")
                    eta_min = int(parts[0].strip())
                    eta_max = int(parts[1].split()[0].strip())


            record = ScrapeRecord(
                platform=self.platform_name,
                address_id=address_id,
                address_text=address_text,

                restaurant_name=restaurant_name,
                restaurant_id="rappi-no-id",

                category="generic",
                item_name=item_name,
                item_description="",

                final_price=final_price,
                original_price=original_price,
                discount=None,

                delivery_time=f"{eta_min}-{eta_max} min" if eta_min else None,
                delivery_fee=delivery_fee,
                distance_km=None,

                timestamp=datetime.utcnow().isoformat()
            )

            records.append(record)

           
            self.page.go_back()
            self.page.wait_for_timeout(3000)
            take_screenshot(self.page, "rappi_back_to_menu")

        return records