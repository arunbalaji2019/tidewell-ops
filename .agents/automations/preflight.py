"""Preflight check for the tidewell-ops alert-triage Automation.

Reads one tracker webhook delivery (alerts/ALERTS.md) from $EVENT_FILE and
writes one item per event to $OUTPUT_FILE. Item id = fingerprint, so the
platform never starts a second session for a fingerprint it has already run.
Customer data is removed from each event's `sample` before any session sees it:
text values become "<redacted>" unless their key is in SAFE_TEXT_KEYS, numbers
and booleans are kept, and every key is kept. Emails are also scrubbed from all
other text fields.
"""
import json
import os
import re

SAFE_TEXT_KEYS = {"sku", "country", "currency", "template"}
SENSITIVE_NUMBER_KEY = re.compile(r"card|phone|account|iban", re.I)
FINGERPRINT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
REDACTED = "<redacted>"
TEXT_FIELDS = ("service", "level", "title", "culprit", "first_seen", "last_seen")


def redact(value, key=""):
    if isinstance(value, dict):
        return {k: redact(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v, key) for v in value]
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return REDACTED if SENSITIVE_NUMBER_KEY.search(key) else value
    if key in SAFE_TEXT_KEYS and isinstance(value, str) and not EMAIL.search(value):
        return value
    return REDACTED


def scrub(text):
    return EMAIL.sub("<email>", str(text))[:500]


def build_output(event):
    body = (event.get("payload") or {}).get("body")
    if not isinstance(body, dict) or not isinstance(body.get("events"), list):
        return {"run": False, "reason": "body is not a tracker delivery with an events list"}
    items = {}
    for alert in body["events"]:
        fingerprint = alert.get("fingerprint") if isinstance(alert, dict) else None
        if not isinstance(fingerprint, str) or not FINGERPRINT.match(fingerprint):
            continue
        count = alert.get("count") if isinstance(alert.get("count"), int) else 0
        if fingerprint in items and items[fingerprint]["count"] >= count:
            continue
        item = {"id": fingerprint, "fingerprint": fingerprint}
        item.update({field: scrub(alert.get(field, "")) for field in TEXT_FIELDS})
        item["count"] = count
        item["sent_at"] = scrub(body.get("sent_at", ""))
        item["sample"] = redact(alert.get("sample") or {})
        items[fingerprint] = item
    return {"items": list(items.values())}


def main():
    with open(os.environ["EVENT_FILE"]) as f:
        event = json.load(f)
    with open(os.environ["OUTPUT_FILE"], "w") as f:
        json.dump(build_output(event), f)


if __name__ == "__main__":
    main()
