VAT_RATE = 0.20


def order_total(lines, discount_pence=0):
    """lines: list of (unit_price_pence, qty). Returns total in pence incl. VAT."""
    net = sum(price * qty for price, qty in lines) - discount_pence
    if net < 0:
        net = 0
    return round(net * (1 + VAT_RATE))
