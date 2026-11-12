from services.shipping.rates import quote


def test_uk_highlands():
    assert quote({"country": "GB", "postcode": "IV2 3AB"}, 1) == 6.95


def test_france():
    assert quote({"country": "FR", "postcode": "75001"}, 2) == 10.75


def test_ireland_without_postcode():
    address = {
        "country": "IE",
        "name": "Test Customer",
        "line1": "1 Example Road",
        "city": "Testtown",
    }
    assert quote(address, 2.4) == 9.57
