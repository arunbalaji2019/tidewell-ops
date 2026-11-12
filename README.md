# tidewell-ops

Backend services for Tidewell Outdoor (online outdoor-gear shop, ~40k orders/month).
Python 3.11, pytest. Five services live in this repo:

| Service | What it does | Owner |
|---|---|---|
| `services/orders` | order creation and totals | Platform |
| `services/inventory` | stock levels and holds | Platform |
| `services/shipping` | shipping quotes | Platform |
| `services/notifications` | order emails | Platform |
| `services/payments` | refunds and captures | **Payments team** (see CODEOWNERS) |

Errors from production go to our error tracker, which can POST alerts to a
webhook. The payload format is in `alerts/ALERTS.md`.
