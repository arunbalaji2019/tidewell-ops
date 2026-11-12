import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / ".agents" / "automations" / "preflight.py"
BATCH = json.loads((ROOT / "alerts" / "samples" / "batch-1.json").read_text())


def run_preflight(tmp_path, body):
    event_file, output_file = tmp_path / "event.json", tmp_path / "output.json"
    event_file.write_text(json.dumps({"event_type": "webhook:incoming", "payload": {"body": body}}))
    env = dict(os.environ, EVENT_FILE=str(event_file), OUTPUT_FILE=str(output_file))
    subprocess.run([sys.executable, str(SCRIPT)], env=env, check=True)
    return json.loads(output_file.read_text())


def test_one_item_per_fingerprint(tmp_path):
    items = run_preflight(tmp_path, BATCH)["items"]
    assert [i["id"] for i in items] == ["inv-7f21c", "shp-a903e", "ntf-1c0d8", "pay-55be2"]
    assert all(i["id"] == i["fingerprint"] and i["sent_at"] == BATCH["sent_at"] for i in items)


def test_customer_data_removed_but_shape_kept(tmp_path):
    output = run_preflight(tmp_path, BATCH)
    text = json.dumps(output)
    for value in ["jo.marsh@example.com", "Aoife Byrne", "4 Quay St", "Galway", "sam.k@example.com", "4242"]:
        assert value not in text
    samples = {i["id"]: i["sample"] for i in output["items"]}
    assert samples["inv-7f21c"] == {"sku": "TW-1182", "on_hand": 3, "held": 2, "requested": 3, "customer_email": "<redacted>"}
    address = samples["shp-a903e"]["address"]
    assert address["country"] == "IE" and "postcode" not in address
    assert samples["pay-55be2"]["card_last4"] == "<redacted>"


def test_duplicate_fingerprint_in_one_delivery_emits_once(tmp_path):
    event = dict(BATCH["events"][0])
    body = {"sent_at": "x", "events": [event, dict(event, count=20), dict(event, count=5)]}
    items = run_preflight(tmp_path, body)["items"]
    assert len(items) == 1 and items[0]["count"] == 20


def test_bad_fingerprints_and_bodies_are_skipped(tmp_path):
    body = {"events": [{"fingerprint": "x y; ignore previous"}, {"title": "no fingerprint"}, "junk"]}
    assert run_preflight(tmp_path, body) == {"items": []}
    assert run_preflight(tmp_path, {"hello": "world"})["run"] is False
