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
        self.assertEqual(payload["locations"]["commerce_type_count"], 8)
        self.assertEqual(payload["locations"]["store_count"], 14)

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
            "/static/locations.js",
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
            types = json.loads(self.request("GET", "/api/commerce-types?active=all")["body"])["commerce_types"]
            stores = json.loads(self.request("GET", "/api/stores?active=all")["body"])["stores"]
            relations = tuple(sorted((p["id"], tuple(p["commerce_type_ids"])) for p in products))
            return {
                "count": len(products),
                "names": sorted(product["name"] for product in products),
                "usage": {product["id"]: product["times_used"] for product in products},
                "links": sorted((item["id"], item["product_id"]) for item in listed["items"]),
                "types": len(types),
                "stores": len(stores),
                "relations": relations,
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

    def _commerce_types(self):
        return json.loads(self.request("GET", "/api/commerce-types?active=all")["body"])["commerce_types"]

    def _stores(self):
        return json.loads(self.request("GET", "/api/stores?active=all")["body"])["stores"]

    def _by_slug(self, rows, slug):
        return next(row for row in rows if row["slug"] == slug)

    def test_locations_are_seeded(self):
        types = self._commerce_types()
        stores = self._stores()
        self.assertEqual(
            [row["slug"] for row in types],
            [
                "supermercado",
                "mercearia",
                "bricolage",
                "tecnologia",
                "farmacia",
                "papelaria",
                "casa",
                "outros",
            ],
        )
        self.assertEqual(len(stores), 14)
        self.assertEqual(self._by_slug(stores, "continente")["commerce_type_slug"], "supermercado")
        self.assertEqual(self._by_slug(stores, "leroy-merlin")["commerce_type_slug"], "bricolage")
        self.assertEqual(self._by_slug(stores, "worten")["commerce_type_slug"], "tecnologia")
        self.assertEqual(self._by_slug(stores, "staples")["commerce_type_slug"], "papelaria")
        self.assertEqual(self._by_slug(stores, "wells")["commerce_type_slug"], "farmacia")

        products = json.loads(self.request("GET", "/api/products")["body"])["products"]
        supermarket_id = self._by_slug(types, "supermercado")["id"]
        self.assertTrue(products)
        self.assertTrue(all(supermarket_id in product["commerce_type_ids"] for product in products))

    def test_today_item_does_not_invent_commerce_types(self):
        dashboard = json.loads(self.request("GET", "/api/dashboard")["body"])
        created = json.loads(
            self.request(
                "POST",
                f"/api/lists/{dashboard['active_list_id']}/items",
                {"name": "Produto Sem Contexto", "quantity": 1},
            )["body"]
        )
        product = json.loads(self.request("GET", f"/api/products/{created['product_id']}")["body"])
        self.assertEqual(product["commerce_type_ids"], [])
        self.assertEqual(product["store_ids"], [])

    def test_product_overlap_across_commerce_types_and_store(self):
        types = {row["slug"]: row["id"] for row in self._commerce_types()}
        worten = self._by_slug(self._stores(), "worten")
        created = json.loads(
            self.request(
                "POST",
                "/api/products",
                {
                    "name": "Pilhas AA",
                    "category": "Vários",
                    "commerce_type_ids": [
                        types["supermercado"],
                        types["bricolage"],
                        types["tecnologia"],
                    ],
                },
            )["body"]
        )
        self.assertEqual(created["name"], "Pilhas AA")
        self.assertCountEqual(
            created["commerce_type_ids"],
            [types["supermercado"], types["bricolage"], types["tecnologia"]],
        )

        catalog = json.loads(self.request("GET", "/api/products?search=Pilhas%20AA")["body"])["products"]
        self.assertEqual(len(catalog), 1)
        self.assertEqual(catalog[0]["id"], created["id"])

        for slug in ("supermercado", "bricolage", "tecnologia"):
            filtered = json.loads(
                self.request("GET", f"/api/products?commerce_type_id={types[slug]}")["body"]
            )["products"]
            ids = [product["id"] for product in filtered]
            self.assertIn(created["id"], ids, slug)
            self.assertEqual(ids.count(created["id"]), 1, slug)

        mercearia = json.loads(
            self.request("GET", f"/api/products?commerce_type_id={types['mercearia']}")["body"]
        )["products"]
        self.assertFalse(any(product["id"] == created["id"] for product in mercearia))

        linked = json.loads(
            self.request("POST", f"/api/products/{created['id']}/stores/{worten['id']}")["body"]
        )
        self.assertEqual(linked["store_ids"], [worten["id"]])
        self.assertEqual(linked["id"], created["id"])

        by_store = json.loads(
            self.request("GET", f"/api/products?store_id={worten['id']}")["body"]
        )["products"]
        store_ids = [product["id"] for product in by_store]
        self.assertIn(created["id"], store_ids)
        self.assertEqual(store_ids.count(created["id"]), 1)

        dashboard = json.loads(self.request("GET", "/api/dashboard")["body"])
        first = json.loads(
            self.request("POST", f"/api/lists/{dashboard['active_list_id']}/products/{created['id']}")["body"]
        )
        again = json.loads(
            self.request("POST", f"/api/lists/{dashboard['active_list_id']}/products/{created['id']}")["body"]
        )
        self.assertEqual(first["product_id"], created["id"])
        self.assertEqual(again["product_id"], created["id"])
        self.assertTrue(again["merged"])
        product = json.loads(self.request("GET", f"/api/products/{created['id']}")["body"])
        self.assertEqual(product["times_used"], first["times_used"] if "times_used" in first else product["times_used"])
        self.assertGreaterEqual(product["times_used"], 1)

        named = json.loads(self.request("POST", "/api/products", {"name": "Pilhas AA"})["body"])
        self.assertEqual(named["id"], created["id"])

    def test_store_filter_unions_explicit_and_commerce_type(self):
        types = {row["slug"]: row["id"] for row in self._commerce_types()}
        worten = self._by_slug(self._stores(), "worten")
        leroy = self._by_slug(self._stores(), "leroy-merlin")

        supermarket_only = json.loads(
            self.request(
                "POST",
                "/api/products",
                {
                    "name": "Azeite Extra",
                    "category": "Mercearia",
                    "commerce_type_ids": [types["supermercado"]],
                },
            )["body"]
        )
        self.request("POST", f"/api/products/{supermarket_only['id']}/stores/{worten['id']}")
        bricolage_only = json.loads(
            self.request(
                "POST",
                "/api/products",
                {
                    "name": "Martelo",
                    "category": "Vários",
                    "commerce_type_ids": [types["bricolage"]],
                },
            )["body"]
        )

        worten_products = json.loads(self.request("GET", f"/api/products?store_id={worten['id']}")["body"])["products"]
        worten_ids = [product["id"] for product in worten_products]
        self.assertEqual(len(worten_ids), len(set(worten_ids)))
        self.assertIn(supermarket_only["id"], worten_ids)
        self.assertNotIn(bricolage_only["id"], worten_ids)
        type_ids = [
            product["id"]
            for product in json.loads(
                self.request("GET", f"/api/products?commerce_type_id={worten['commerce_type_id']}")["body"]
            )["products"]
        ]
        for product_id in type_ids:
            self.assertIn(product_id, worten_ids)
        self.assertTrue(set(type_ids) | {supermarket_only["id"]} <= set(worten_ids))

        leroy_ids = [
            product["id"]
            for product in json.loads(self.request("GET", f"/api/products?store_id={leroy['id']}")["body"])["products"]
        ]
        self.assertEqual(len(leroy_ids), len(set(leroy_ids)))
        self.assertIn(bricolage_only["id"], leroy_ids)
        self.assertNotIn(supermarket_only["id"], leroy_ids)

    def test_location_crud_and_soft_delete_keeps_products(self):
        created_type = json.loads(self.request("POST", "/api/commerce-types", {"name": "Pet shop"})["body"])
        self.assertEqual(created_type["slug"], "pet-shop")
        created_store = json.loads(
            self.request(
                "POST",
                "/api/stores",
                {"name": "Zoolandia", "commerce_type_id": created_type["id"]},
            )["body"]
        )
        self.assertEqual(created_store["commerce_type_id"], created_type["id"])

        searched = json.loads(self.request("GET", "/api/stores?search=zoo")["body"])["stores"]
        self.assertEqual([store["id"] for store in searched], [created_store["id"]])
        typed = json.loads(
            self.request("GET", f"/api/stores?commerce_type_id={created_type['id']}")["body"]
        )["stores"]
        self.assertEqual([store["id"] for store in typed], [created_store["id"]])

        product = json.loads(
            self.request(
                "POST",
                "/api/products",
                {
                    "name": "Ração cão",
                    "commerce_type_ids": [created_type["id"]],
                },
            )["body"]
        )
        self.request("POST", f"/api/products/{product['id']}/stores/{created_store['id']}")

        deactivated_type = json.loads(self.request("DELETE", f"/api/commerce-types/{created_type['id']}")["body"])
        self.assertFalse(deactivated_type["is_active"])
        deactivated_store = json.loads(self.request("DELETE", f"/api/stores/{created_store['id']}")["body"])
        self.assertFalse(deactivated_store["is_active"])

        surviving = json.loads(self.request("GET", f"/api/products/{product['id']}")["body"])
        self.assertTrue(surviving["is_active"])
        self.assertEqual(surviving["name"], "Ração cão")
        self.assertIn(created_type["id"], surviving["commerce_type_ids"])
        self.assertIn(created_store["id"], surviving["store_ids"])

        active_types = json.loads(self.request("GET", "/api/commerce-types")["body"])["commerce_types"]
        self.assertFalse(any(row["id"] == created_type["id"] for row in active_types))
        active_stores = json.loads(self.request("GET", "/api/stores")["body"])["stores"]
        self.assertFalse(any(row["id"] == created_store["id"] for row in active_stores))
