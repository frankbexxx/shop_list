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

        query = ""
        if "?" in path:
            path, query = path.split("?", 1)

        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "CONTENT_LENGTH": str(len(body)),
            "wsgi.input": io.BytesIO(body),
            "QUERY_STRING": query,
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
        self.assertIn(b"Shopping List", response["body"])
        self.assertIn(b"app-shell", response["body"])
        self.assertIn(b"bottom-nav", response["body"])

    def test_shell_assets_respond(self):
        for path in (
            "/static/design-tokens.css",
            "/static/themes.css",
            "/static/styles.css",
            "/static/theme.js",
            "/static/navigation.js",
            "/static/app.js",
            "/static/catalog.js",
        ):
            response = self.request("GET", path)
            self.assertEqual(response["status"], "200 OK", path)

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

    def test_templates_migrate_into_products(self):
        products = json.loads(self.request("GET", "/api/products")["body"])["products"]
        names = {product["name"].lower() for product in products}
        self.assertGreaterEqual(len(products), 6)
        self.assertIn("milk", names)
        self.assertTrue(all(product["is_active"] for product in products))

        dashboard = json.loads(self.request("GET", "/api/dashboard")["body"])
        list_payload = json.loads(self.request("GET", f"/api/lists/{dashboard['active_list_id']}")["body"])
        self.assertTrue(all(item.get("product_id") for item in list_payload["items"]))

    def test_bootstrap_is_idempotent(self):
        def snapshot():
            products = json.loads(self.request("GET", "/api/products?active=all")["body"])["products"]
            dashboard = json.loads(self.request("GET", "/api/dashboard")["body"])
            listed = json.loads(self.request("GET", f"/api/lists/{dashboard['active_list_id']}")["body"])
            return {
                "count": len(products),
                "names": sorted(product["name"] for product in products),
                "usage": {product["id"]: product["times_used"] for product in products},
                "links": sorted((item["id"], item["product_id"]) for item in listed["items"]),
            }

        first = snapshot()
        ShoppingApplication(self.db_path)
        second = snapshot()
        ShoppingApplication(self.db_path)
        third = snapshot()
        self.assertEqual(first, second)
        self.assertEqual(second, third)

    def test_product_name_normalization_reuses_same_row(self):
        first = self.request("POST", "/api/products", {"name": "Arroz", "category": "Mercearia"})
        product = json.loads(first["body"])
        self.assertEqual(first["status"], "201 Created")

        for name in (" arroz ", "ARROZ", "ArRoZ"):
            response = self.request("POST", "/api/products", {"name": name, "category": "Mercearia"})
            payload = json.loads(response["body"])
            self.assertEqual(response["status"], "200 OK", name)
            self.assertEqual(payload["id"], product["id"], name)
            self.assertEqual(payload["name"], "Arroz", name)

        catalog = json.loads(self.request("GET", "/api/products?search=arroz")["body"])["products"]
        matches = [item for item in catalog if item["id"] == product["id"]]
        self.assertEqual(len(matches), 1)

    def test_product_catalog_crud(self):
        created = self.request("POST", "/api/products", {"name": "Arroz", "category": "Mercearia"})
        product = json.loads(created["body"])
        self.assertEqual(created["status"], "201 Created")
        self.assertEqual(product["name"], "Arroz")

        listed = json.loads(self.request("GET", "/api/products?search=arroz")["body"])["products"]
        self.assertTrue(any(item["id"] == product["id"] for item in listed))

        patched = json.loads(
            self.request("PATCH", f"/api/products/{product['id']}", {"default_unit": "kg"})["body"]
        )
        self.assertEqual(patched["default_unit"], "kg")

        deactivated = json.loads(self.request("DELETE", f"/api/products/{product['id']}")["body"])
        self.assertFalse(deactivated["is_active"])
        remaining = json.loads(self.request("GET", "/api/products")["body"])["products"]
        self.assertFalse(any(item["id"] == product["id"] for item in remaining))

    def test_selecting_product_adds_to_today_without_duplicate(self):
        product = json.loads(self.request("POST", "/api/products", {"name": "Arroz Carolino"})["body"])
        dashboard = json.loads(self.request("GET", "/api/dashboard")["body"])
        list_id = dashboard["active_list_id"]

        first = self.request("POST", f"/api/lists/{list_id}/products/{product['id']}", {"quantity": 1})
        self.assertEqual(first["status"], "201 Created")
        second = self.request("POST", f"/api/lists/{list_id}/products/{product['id']}", {"quantity": 2})
        self.assertEqual(second["status"], "200 OK")
        merged = json.loads(second["body"])
        self.assertTrue(merged["merged"])
        self.assertEqual(merged["quantity"], 3)

        listed = json.loads(self.request("GET", f"/api/lists/{list_id}")["body"])
        matches = [item for item in listed["items"] if item["product_id"] == product["id"]]
        self.assertEqual(len(matches), 1)

    def test_adding_unknown_item_creates_catalog_product(self):
        dashboard = json.loads(self.request("GET", "/api/dashboard")["body"])
        list_id = dashboard["active_list_id"]
        created = json.loads(
            self.request(
                "POST",
                f"/api/lists/{list_id}/items",
                {"name": "  PILHAS CR2032 ", "quantity": 1, "category": "Vários"},
            )["body"]
        )
        self.assertIsNotNone(created["product_id"])
        product = json.loads(self.request("GET", f"/api/products/{created['product_id']}")["body"])
        self.assertEqual(product["name"], "PILHAS CR2032")

        again = json.loads(
            self.request("POST", f"/api/lists/{list_id}/items", {"name": "pilhas cr2032", "quantity": 1})["body"]
        )
        self.assertTrue(again["merged"])
        self.assertEqual(again["product_id"], created["product_id"])

    def test_product_survives_removing_from_today(self):
        product = json.loads(self.request("POST", "/api/products", {"name": "Detergente roupa"})["body"])
        dashboard = json.loads(self.request("GET", "/api/dashboard")["body"])
        list_id = dashboard["active_list_id"]
        item = json.loads(self.request("POST", f"/api/lists/{list_id}/products/{product['id']}")["body"])
        self.request("DELETE", f"/api/items/{item['id']}")
        surviving = json.loads(self.request("GET", f"/api/products/{product['id']}")["body"])
        self.assertTrue(surviving["is_active"])
        listed = json.loads(self.request("GET", f"/api/lists/{list_id}")["body"])
        self.assertFalse(any(row["id"] == item["id"] for row in listed["items"]))
