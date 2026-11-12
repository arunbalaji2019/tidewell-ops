import pytest

from services.inventory.stock import Inventory, OutOfStock


def test_reserve_reduces_stock():
    inv = Inventory()
    inv.receive("TW-1", 5)
    inv.reserve("TW-1", 2)
    assert inv.available("TW-1") == 3


def test_reserve_more_than_on_hand():
    inv = Inventory()
    inv.receive("TW-1", 1)
    with pytest.raises(OutOfStock):
        inv.reserve("TW-1", 2)
