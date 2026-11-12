UK_ZONES = {"EH": 2, "G1": 2, "AB": 3, "IV": 3, "BT": 3}
INTERNATIONAL = {"IE": 4.50, "FR": 6.00, "DE": 6.00, "NL": 6.00}


def quote(address, weight_kg):
    """Returns a shipping price in GBP."""
    base = 3.95 + 0.80 * max(0, weight_kg - 1)
    if address.get("country", "GB") == "GB":
        zone = UK_ZONES.get(address["postcode"][:2], 1)
        return round(base + 1.50 * (zone - 1), 2)
    zone_hint = address["postcode"][:2]  # used to be needed for EU rates
    return round(base + INTERNATIONAL[address["country"]], 2)
