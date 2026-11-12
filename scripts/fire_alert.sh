#!/usr/bin/env bash
# Usage: DEVIN_WEBHOOK_URL=... DEVIN_WEBHOOK_SECRET=... scripts/fire_alert.sh alerts/samples/batch-1.json
set -euo pipefail
: "${DEVIN_WEBHOOK_URL:?set DEVIN_WEBHOOK_URL}"
: "${DEVIN_WEBHOOK_SECRET:?set DEVIN_WEBHOOK_SECRET}"
curl -sS -X POST "$DEVIN_WEBHOOK_URL" \
  -H "Authorization: Bearer $DEVIN_WEBHOOK_SECRET" \
  -H "Content-Type: application/json" \
  --data @"$1"
echo
