from services.orders.totals import order_total


def test_total_with_vat():
    assert order_total([(1000, 2), (500, 1)]) == 3000


def test_discount_floor():
    assert order_total([(100, 1)], discount_pence=500) == 0
