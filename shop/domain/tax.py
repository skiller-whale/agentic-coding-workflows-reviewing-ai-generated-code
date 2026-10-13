from shop.domain.money import Money

VAT_PERCENT = 20


def vat_included_in(amount: Money) -> Money:
    """The VAT included in `amount`. Prices include VAT."""
    return amount.fraction(VAT_PERCENT, 100 + VAT_PERCENT)
