from shop.domain.money import ZERO, Money

STANDARD_RATE = Money(495)


def shipping_for(merchandise: Money, free_shipping_threshold: Money) -> Money:
    """Shipping is free when the merchandise (before any adjustments) reaches the threshold."""
    if merchandise >= free_shipping_threshold:
        return ZERO
    return STANDARD_RATE
