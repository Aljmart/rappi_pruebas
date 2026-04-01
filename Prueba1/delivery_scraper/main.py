import json
import multiprocessing as mp
from pathlib import Path
import csv

from playwright.sync_api import sync_playwright

from scrapers.ubereats_scraper import UberEatsScraper
from scrapers.rappi_scraper import RappiScraper
from scrapers.didi_scraper import DidiScraper

from models.record import ScrapeRecord


OUTPUT_CSV = Path("output/data.csv")

PLATFORMS = [
    ("ubereats", UberEatsScraper),
    ("rappi", RappiScraper),
    ("didi", DidiScraper),
]


def load_addresses():
    with open("config/addresses.json", "r", encoding="utf-8") as f:
        return json.load(f)


def run_address_job(address):
    addr_id = address["id"]
    addr_text = address["text"]

    print(f"\n=== Procesando dirección {addr_id}: {addr_text} ===")

    all_records = []

    with sync_playwright() as p:

        for platform_name, ScraperClass in PLATFORMS:

            print(f"[{addr_id}] Ejecutando {platform_name}...")

            
            browser = p.chromium.launch(
                headless=False,  # Rappi y DiDi bloquean headless
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-site-isolation-trials",
                ]
            )

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                locale="es-MX",
                timezone_id="America/Mexico_City",
                geolocation={"latitude": 19.4326, "longitude": -99.1332},
                permissions=["geolocation"],
                viewport={"width": 1280, "height": 720},
            )

            page = context.new_page()

         
            page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['es-MX', 'es']});
            """)
            scraper = ScraperClass(page)

            try:
                records = scraper.scrape_address(addr_id, addr_text)
                all_records.extend(records)
            except Exception as e:
                print(f"Error en {platform_name} / {addr_id}: {e}")

            page.close()
            browser.close()

    return all_records


def main():
    addresses = load_addresses()
    print(f"Procesando {len(addresses)} direcciones en paralelo...\n")

    with mp.Pool(processes=4) as pool:
        results = pool.map(run_address_job, addresses)

    all_records = []
    for rec_list in results:
        all_records.extend(rec_list)

    if not all_records:
        print("No se obtuvieron registros.")
        return

    rows = [r.__dict__ for r in all_records]
    fieldnames = rows[0].keys()

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nExportado {len(all_records)} registros a {OUTPUT_CSV}")


if __name__ == "__main__":
    mp.set_start_method("spawn")
    main()
