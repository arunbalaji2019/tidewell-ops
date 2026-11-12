from services.shipping.rates import quote


def test_uk_highlands():
    assert quote({"country": "GB", "postcode": "IV2 3AB"}, 1) == 6.95


def test_france():
    assert quote({"country": "FR", "postcode": "75001"}, 2) == 10.75
