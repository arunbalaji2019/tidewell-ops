from services.payments.refunds import partial_refund


def test_half_refund():
    assert partial_refund(2000, 50) == 1000
