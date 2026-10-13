from dataclasses import dataclass

from shop.domain.errors import ValidationFailed
from shop.domain.models import Adjustment, OrderLine
from shop.domain.money import Money
from shop.domain.shipping import shipping_for
from shop.domain.tax import vat_included_in


@dataclass(frozen=True)
class PriceBreakdown:
    merchandise: Money
    adjustments: list[Adjustment]
    tax: Money
    shipping: Money
    total: Money

    @property
    def reductions(self) -> Money:
        return Money.sum(adjustment.amount for adjustment in self.adjustments)

    @property
    def taxable(self) -> Money:
        return self.merchandise - self.reductions


def price(
    lines: list[OrderLine], adjustments: list[Adjustment], free_shipping_threshold: Money
) -> PriceBreakdown:
    """Work out what an order costs.

    Adjustments come off the merchandise before tax. Shipping is judged on the merchandise
    before adjustments, so an adjustment never costs the customer their free shipping.
    """
    merchandise = Money.sum(line.line_total for line in lines)
    reductions = Money.sum(adjustment.amount for adjustment in adjustments)
    if reductions > merchandise:
        raise ValidationFailed("Adjustments can't come to more than the merchandise")

    taxable = merchandise - reductions
    shipping = shipping_for(merchandise, free_shipping_threshold)
    return PriceBreakdown(
        merchandise=merchandise,
        adjustments=list(adjustments),
        tax=vat_included_in(taxable),
        shipping=shipping,
        total=taxable + shipping,
    )
