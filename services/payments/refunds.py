class RefundMismatch(Exception):
    pass


def partial_refund(order_total_pence, percent):
    """Refund a percentage of an order. Payments team owns this (PCI scope)."""
    return int(order_total_pence * percent / 100)
