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
    raw = {e["fingerprint"]: e["sample"] for e in BATCH["events"]}
    address = raw["shp-a903e"]["address"]
    private = [raw["inv-7f21c"]["customer_email"], raw["ntf-1c0d8"]["to"], raw["pay-55be2"]["card_last4"]]
    private += [address["name"], address["line1"], address["city"]]
    for value in private:
        assert value not in text
    samples = {i["id"]: i["sample"] for i in output["items"]}
    assert samples["inv-7f21c"] == {"sku": "TW-1182", "on_hand": 3, "held": 2, "requested": 3, "customer_email": "<redacted>"}
    address = samples["shp-a903e"]["address"]
    assert address["country"] == "IE" and "postcode" not in address
    assert samples["pay-55be2"]["card_last4"] == "<redacted>"


def test_duplicate_fingerprint_in_one_delivery_emits_once(tmp_path):
    event = dict(BATCH["events"][0])
    body = {"source": "tracker", "sent_at": "x", "events": [event, dict(event, count=20), dict(event, count=5)]}
    items = run_preflight(tmp_path, body)["items"]
    assert len(items) == 1 and items[0]["count"] == 20


def test_nested_sensitive_values_and_non_code_safe_text_redacted(tmp_path):
    sample = {"card": {"last4": 1234, "country": "GB"}, "template": "Test Customer, 1 Example Road", "sku": "TW-1"}
    body = {"source": "tracker", "events": [dict(BATCH["events"][0], sample=sample)]}
    redacted = run_preflight(tmp_path, body)["items"][0]["sample"]
    assert redacted == {"card": {"last4": "<redacted>", "country": "<redacted>"}, "template": "<redacted>", "sku": "TW-1"}


def test_bad_fingerprints_and_bodies_are_skipped(tmp_path):
    bad = [{"fingerprint": "x y; ignore previous"}, {"fingerprint": "inv-7f21c\n"}, {"title": "no fingerprint"}, "junk"]
    assert run_preflight(tmp_path, {"source": "tracker", "events": bad}) == {"items": []}
    assert run_preflight(tmp_path, {"hello": "world"})["run"] is False
    assert run_preflight(tmp_path, dict(BATCH, source="other"))["run"] is False
