import io
import json
import unittest
from pathlib import Path
from uuid import uuid4

from supermarket_app.server import ShoppingApplication


class WSGITestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.db_path = Path("data") / f"test-{uuid4().hex}.sqlite3"
        self.app = ShoppingApplication(self.db_path)

    def tearDown(self) -> None:
        if self.db_path.exists():
            self.db_path.unlink()

    def request(self, method: str, path: str, payload: dict | None = None):
        body = b""
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = headers

        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "CONTENT_LENGTH": str(len(body)),
            "wsgi.input": io.BytesIO(body),
            "QUERY_STRING": "",
        }
        response = b"".join(self.app(environ, start_response))
        captured["body"] = response
        return captured

    def test_dashboard_bootstraps_default_list(self):
        response = self.request("GET", "/api/dashboard")
        payload = json.loads(response["body"])
        self.assertEqual(response["status"], "200 OK")
        self.assertGreaterEqual(len(payload["lists"]), 1)
        self.assertGreaterEqual(len(payload["suggestions"]), 1)

    def test_root_serves_frontend(self):
        response = self.request("GET", "/")
        self.assertEqual(response["status"], "200 OK")
        self.assertIn(b"Market Flow", response["body"])

    def test_can_create_list_and_item(self):
        created_list = self.request(
            "POST",
            "/api/lists",
            {"name": "Saturday Run", "store_name": "Mercado", "budget": 55},
        )
        list_payload = json.loads(created_list["body"])
        self.assertEqual(created_list["status"], "201 Created")

        created_item = self.request(
            "POST",
            f"/api/lists/{list_payload['id']}/items",
            {"name": "Tomatoes", "quantity": 2, "unit": "kg", "aisle": "Produce", "estimated_price": 2.5},
        )
        item_payload = json.loads(created_item["body"])
        self.assertEqual(created_item["status"], "201 Created")
        self.assertEqual(item_payload["name"], "Tomatoes")

        loaded = self.request("GET", f"/api/lists/{list_payload['id']}")
        loaded_payload = json.loads(loaded["body"])
        self.assertEqual(len(loaded_payload["items"]), 1)
        self.assertEqual(loaded_payload["summary"]["estimated_total"], 5.0)

    def test_cycle_item_status(self):
        dashboard = json.loads(self.request("GET", "/api/dashboard")["body"])
        list_id = dashboard["active_list_id"]
        list_payload = json.loads(self.request("GET", f"/api/lists/{list_id}")["body"])
        item_id = list_payload["items"][0]["id"]

        cycled = self.request("POST", f"/api/items/{item_id}/cycle")
        payload = json.loads(cycled["body"])
        self.assertEqual(payload["status"], "in_cart")

        cycled = self.request("POST", f"/api/items/{item_id}/cycle")
        payload = json.loads(cycled["body"])
        self.assertEqual(payload["status"], "purchased")
