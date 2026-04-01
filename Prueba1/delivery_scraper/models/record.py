from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class ScrapeRecord:
    platform: str
    address_id: str
    address_text: str
    restaurant_name: str
    item_name: str
    item_price: Optional[float]
    delivery_fee: Optional[float]
    service_fee: Optional[float]
    eta_min: Optional[int]
    eta_max: Optional[int]
    discount_text: Optional[str]
    availability: Optional[str]
    final_price: Optional[float]
    timestamp: str

    def to_dict(self):
        return asdict(self)