import os
from dataclasses import dataclass

from shop.domain.money import Money


@dataclass(frozen=True)
class Settings:
    database: str = ":memory:"
    free_shipping_threshold: Money = Money(5000)
    loyalty_points_per_pound: int = 1
    loyalty_point_value: Money = Money(1)
    loyalty_max_redemption_percent: int = 50


def load_settings() -> Settings:
    return Settings(database=os.environ.get("SHOP_DATABASE", Settings.database))
