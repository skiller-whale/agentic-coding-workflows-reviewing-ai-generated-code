from shop.money import Money


def test_parse_and_format():
    assert Money.parse("12.50") == Money(1250)
    assert str(Money(1250)) == "12.50"
    assert str(Money(5)) == "0.05"

