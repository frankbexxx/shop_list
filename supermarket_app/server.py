import argparse
import json
import webbrowser
from pathlib import Path
from wsgiref.simple_server import make_server

from .config import BASE_DIR, DEFAULT_DB_PATH, DEFAULT_HOST, DEFAULT_PORT
from .database import Database
from .seed import load_seed_data
from .services import ShoppingService
from .web import HTTPError, get_query, json_response, parse_json_body, parse_path_params, serve_static


class ShoppingApplication:
    def __init__(self, db_path: Path | None = None) -> None:
        self.database = Database(db_path or DEFAULT_DB_PATH)
        self.service = ShoppingService(self.database)
        categories, templates = load_seed_data(BASE_DIR)
        self.service.bootstrap(categories, templates)

    def __call__(self, environ, start_response):
        method = environ["REQUEST_METHOD"].upper()
        path = environ.get("PATH_INFO", "/") or "/"
        if path != "/":
            path = path.rstrip("/")
        try:
            if path == "/":
                return serve_static("/static/index.html", start_response)
            if path.startswith("/static/"):
                return serve_static(path, start_response)
            if path == "/api/health" and method == "GET":
                return json_response(start_response, {"status": "ok"})
            if path == "/api/dashboard" and method == "GET":
                return json_response(start_response, self.service.dashboard())
            if path == "/api/lists" and method == "GET":
                return json_response(start_response, {"lists": self.service.list_lists()})
            if path == "/api/lists" and method == "POST":
                return json_response(start_response, self.service.create_list(parse_json_body(environ)), "201 Created")
            if path == "/api/suggestions" and method == "GET":
                query = get_query(environ)
                limit = int((query.get("limit") or ["12"])[0])
                return json_response(start_response, {"suggestions": self.service.suggestions(limit)})
            if path == "/api/products" and method == "GET":
                return json_response(start_response, {"products": self.service.list_products(get_query(environ))})
            if path == "/api/products" and method == "POST":
                product = self.service.create_product(parse_json_body(environ))
                status = "201 Created" if product.pop("_created", True) else "200 OK"
                return json_response(start_response, product, status)
            if path == "/api/commerce-types" and method == "GET":
                return json_response(start_response, {"commerce_types": self.service.list_commerce_types(get_query(environ))})
            if path == "/api/commerce-types" and method == "POST":
                return json_response(start_response, self.service.create_commerce_type(parse_json_body(environ)), "201 Created")
            if path == "/api/stores" and method == "GET":
                return json_response(start_response, {"stores": self.service.list_stores(get_query(environ))})
            if path == "/api/stores" and method == "POST":
                return json_response(start_response, self.service.create_store(parse_json_body(environ)), "201 Created")
            if path == "/api/history" and method == "GET":
                return json_response(start_response, {"history": self.service.list_history(get_query(environ))})

            parts = parse_path_params(path)
            if len(parts) >= 3 and parts[0] == "api" and parts[1] == "commerce-types":
                type_id = int(parts[2])
                if len(parts) == 3 and method == "GET":
                    return json_response(start_response, self.service.get_commerce_type(type_id))
                if len(parts) == 3 and method == "PATCH":
                    return json_response(start_response, self.service.update_commerce_type(type_id, parse_json_body(environ)))
                if len(parts) == 3 and method == "DELETE":
                    return json_response(start_response, self.service.deactivate_commerce_type(type_id))

            if len(parts) >= 3 and parts[0] == "api" and parts[1] == "stores":
                store_id = int(parts[2])
                if len(parts) == 3 and method == "GET":
                    return json_response(start_response, self.service.get_store(store_id))
                if len(parts) == 3 and method == "PATCH":
                    return json_response(start_response, self.service.update_store(store_id, parse_json_body(environ)))
                if len(parts) == 3 and method == "DELETE":
                    return json_response(start_response, self.service.deactivate_store(store_id))

            if len(parts) >= 3 and parts[0] == "api" and parts[1] == "products":
                product_id = int(parts[2])
                if len(parts) == 5 and parts[3] == "commerce-types":
                    type_id = int(parts[4])
                    if method == "POST":
                        return json_response(start_response, self.service.add_product_commerce_type(product_id, type_id), "201 Created")
                    if method == "DELETE":
                        return json_response(start_response, self.service.remove_product_commerce_type(product_id, type_id))
                if len(parts) == 5 and parts[3] == "stores":
                    store_id = int(parts[4])
                    if method == "POST":
                        return json_response(start_response, self.service.add_product_store(product_id, store_id), "201 Created")
                    if method == "DELETE":
                        return json_response(start_response, self.service.remove_product_store(product_id, store_id))
                if len(parts) == 3 and method == "GET":
                    return json_response(start_response, self.service.get_product(product_id))
                if len(parts) == 3 and method == "PATCH":
                    return json_response(start_response, self.service.update_product(product_id, parse_json_body(environ)))
                if len(parts) == 3 and method == "DELETE":
                    return json_response(start_response, self.service.deactivate_product(product_id))

            if len(parts) >= 3 and parts[0] == "api" and parts[1] == "lists":
                list_id = int(parts[2])
                if len(parts) == 3 and method == "GET":
                    return json_response(start_response, self.service.get_list(list_id))
                if len(parts) == 3 and method == "PATCH":
                    return json_response(start_response, self.service.update_list(list_id, parse_json_body(environ)))
                if len(parts) == 3 and method == "DELETE":
                    self.service.delete_list(list_id)
                    return json_response(start_response, {"deleted": True})
                if len(parts) == 4 and parts[3] == "complete" and method == "POST":
                    return json_response(start_response, self.service.complete_list(list_id))
                if len(parts) == 4 and parts[3] == "duplicate" and method == "POST":
                    return json_response(start_response, self.service.duplicate_list(list_id), "201 Created")
                if len(parts) == 4 and parts[3] == "items" and method == "POST":
                    item = self.service.create_item(list_id, parse_json_body(environ))
                    status = "200 OK" if item.get("merged") else "201 Created"
                    return json_response(start_response, item, status)
                if len(parts) == 5 and parts[3] == "products" and method == "POST":
                    product_id = int(parts[4])
                    item = self.service.add_product_to_list(list_id, product_id, parse_json_body(environ))
                    status = "200 OK" if item.get("merged") else "201 Created"
                    return json_response(start_response, item, status)

            if len(parts) >= 3 and parts[0] == "api" and parts[1] == "history":
                history_id = int(parts[2])
                if len(parts) == 3 and method == "GET":
                    return json_response(start_response, self.service.get_history(history_id))
                if len(parts) == 4 and parts[3] == "reuse" and method == "POST":
                    return json_response(start_response, self.service.reuse_history(history_id), "201 Created")

            if len(parts) >= 3 and parts[0] == "api" and parts[1] == "items":
                item_id = int(parts[2])
                if len(parts) == 3 and method == "PATCH":
                    return json_response(start_response, self.service.update_item(item_id, parse_json_body(environ)))
                if len(parts) == 3 and method == "DELETE":
                    self.service.delete_item(item_id)
                    return json_response(start_response, {"deleted": True})
                if len(parts) == 4 and parts[3] == "cycle" and method == "POST":
                    return json_response(start_response, self.service.cycle_item_status(item_id))

            raise HTTPError("404 Not Found", "Route not found")
        except KeyError as error:
            return json_response(start_response, {"error": str(error)}, "404 Not Found")
        except ValueError as error:
            return json_response(start_response, {"error": str(error)}, "400 Bad Request")
        except HTTPError as error:
            return json_response(start_response, {"error": error.message}, error.status)
        except json.JSONDecodeError:
            return json_response(start_response, {"error": "Invalid JSON payload"}, "400 Bad Request")
        except Exception as error:  # pragma: no cover
            return json_response(start_response, {"error": f"Internal server error: {error}"}, "500 Internal Server Error")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the supermarket shopping list app.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--no-browser", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    app = ShoppingApplication(args.db)
    url = f"http://{args.host}:{args.port}"

    with make_server(args.host, args.port, app) as server:
        if not args.no_browser:
            try:
                webbrowser.open(url)
            except Exception:
                pass
        print(f"Shopping list app running at {url}")
        server.serve_forever()
    return 0
