from abc import ABC, abstractmethod
from typing import List
from models.record import ScrapeRecord

class BaseScraper(ABC):

    @abstractmethod
    def scrape_address(self, addr_id: str, addr_text: str) -> List[ScrapeRecord]:
        ...
