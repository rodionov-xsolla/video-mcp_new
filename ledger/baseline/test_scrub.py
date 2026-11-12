"""Tests for scrub.py. Run: python3 -m unittest discover -s ledger/baseline

Every secret-looking value here is built at runtime from repeated characters,
so no real-looking key is stored in the repo.
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrub  # noqa: E402

R = scrub.R
FAKE_JWT = "eyJ" + "a" * 20 + "." + "b" * 30 + "." + "c" * 30
FAKE_TG = "1234567890:" + "A" * 35
FAKE_HEX = "f" * 40


def workflow():
    return {
        "workflow": {
            "id": "wf1",
            "name": "Test",
            "versionId": "v1",
            "settings": {"executionOrder": "v1"},
            "scopes": ["workflow:read"],
            "pinData": {"Some node": [{"json": {"text": "private"}}]},
            "nodes": [
                {
                    "name": "Upload",
                    "type": "n8n-nodes-base.httpRequest",
                    "credentials": {"supabaseApi": {"id": "cred-123", "name": "SUPABASE"}},
                    "parameters": {
                        "url": "https://api.example.com/x?dataset_id=gd_abc&key={{ $json.k }}",
                        "headerParameters": {"parameters": [
                            {"name": "Authorization", "value": "Bearer " + FAKE_JWT},
                            {"name": "Content-Type", "value": "image/jpeg"},
                        ]},
                        "queryParameters": {"parameters": [{"name": "token", "value": FAKE_HEX}]},
                        "jsonHeaders": '{"X-Api-Key": "' + FAKE_HEX + '"}',
                    },
                },
                {
                    "name": "Notify",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {
                        "url": "https://api.telegram.org/bot" + FAKE_TG + "/sendMessage",
                        "jsCode": 'const botToken = "' + FAKE_TG + '";',
                    },
                },
                {
                    "name": "Model",
                    "type": "@n8n/n8n-nodes-langchain.openAi",
                    "parameters": {"modelId": {"value": "gpt-4.1-mini"},
                                   "text": "data:image/png;base64," + "QUJD" * 50},
                },
            ],
        },
        "triggerInfo": "connector-only text",
    }


class ScrubTest(unittest.TestCase):
    def setUp(self):
        self.out = scrub.scrub(workflow())
        self.text = scrub.dump(self.out)
        self.nodes = {n["name"]: n for n in self.out["nodes"]}

    def test_unwraps_connector_output_and_drops_metadata(self):
        self.assertEqual(self.out["id"], "wf1")
        self.assertNotIn("scopes", self.out)
        self.assertNotIn("triggerInfo", self.out)
        self.assertEqual(self.out["pinData"], R)

    def test_header_and_query_values_dropped_names_kept(self):
        p = self.nodes["Upload"]["parameters"]
        self.assertEqual([h["name"] for h in p["headerParameters"]["parameters"]],
                         ["Authorization", "Content-Type"])
        self.assertTrue(all(h["value"] == R for h in p["headerParameters"]["parameters"]))
        self.assertEqual(p["queryParameters"]["parameters"][0]["value"], R)
        self.assertEqual(p["jsonHeaders"], R)

    def test_url_query_literals_redacted_expressions_kept(self):
        url = self.nodes["Upload"]["parameters"]["url"]
        self.assertIn("dataset_id=" + R, url)
        self.assertIn("key={{ $json.k }}", url)

    def test_credentials_by_name_only(self):
        self.assertEqual(self.nodes["Upload"]["credentials"], {"supabaseApi": {"name": "SUPABASE"}})

    def test_telegram_token_glued_to_bot(self):
        self.assertNotIn(FAKE_TG, self.text)
        self.assertIn("/bot" + R + "/sendMessage", self.nodes["Notify"]["parameters"]["url"])

    def test_no_fake_secret_survives(self):
        for s in (FAKE_JWT, FAKE_TG, FAKE_HEX, "cred-123"):
            self.assertNotIn(s, self.text)

    def test_data_url_collapsed(self):
        self.assertEqual(self.nodes["Model"]["parameters"]["text"], "data:image/png;base64," + R)

    def test_deterministic_and_idempotent(self):
        self.assertEqual([n["name"] for n in self.out["nodes"]], ["Model", "Notify", "Upload"])
        self.assertEqual(scrub.dump(scrub.scrub(workflow())), self.text)
        self.assertEqual(scrub.dump(scrub.scrub(json.loads(self.text))), self.text)

    def test_check_flags_raw_and_passes_scrubbed(self):
        with tempfile.TemporaryDirectory() as d:
            raw, clean = os.path.join(d, "raw.json"), os.path.join(d, "clean.json")
            with open(raw, "w") as f:
                json.dump(workflow(), f)
            with open(clean, "w") as f:
                f.write(self.text)
            self.assertGreater(len(scrub.check(raw)), 0)
            self.assertEqual(scrub.check(clean), [])


if __name__ == "__main__":
    unittest.main()
