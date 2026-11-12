# Error tracker alert webhook

When an error group (a "fingerprint") is new, or its event count crosses a
threshold, the tracker POSTs a JSON body to the configured webhook URL. It
re-sends the same fingerprint each time the count goes up, so one bug can
produce many deliveries over a day.

```json
{
  "source": "tracker",
  "sent_at": "2026-11-12T09:14:00Z",
  "events": [
    {
      "fingerprint": "inv-7f21c",
      "service": "inventory",
      "level": "error",
      "title": "AssertionError: available stock went negative",
      "culprit": "services/inventory/stock.py in reserve",
      "count": 14,
      "first_seen": "2026-11-12T07:02:11Z",
      "last_seen": "2026-11-12T09:13:40Z",
      "sample": { "...": "the inputs of one failing call, may include customer data" }
    }
  ]
}
```

One delivery can carry several events. Use `scripts/fire_alert.sh <file>` to
send a sample payload to a webhook.
