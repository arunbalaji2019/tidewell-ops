class OutOfStock(Exception):
    pass


class Inventory:
    def __init__(self):
        self.on_hand = {}
        self.held = {}

    def receive(self, sku, qty):
        self.on_hand[sku] = self.on_hand.get(sku, 0) + qty

    def available(self, sku):
        return self.on_hand.get(sku, 0) - self.held.get(sku, 0)

    def hold(self, sku, qty):
        """Basket hold for 15 minutes while the customer checks out."""
        self.held[sku] = self.held.get(sku, 0) + qty

    def reserve(self, sku, qty):
        """Called when an order is paid. Takes stock off the shelf."""
        if qty > self.on_hand.get(sku, 0):
            raise OutOfStock(sku)
        self.on_hand[sku] -= qty
        assert self.available(sku) >= 0, "available stock went negative"
