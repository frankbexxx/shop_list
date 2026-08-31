from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .database import Database
from .locations import attach_product_contexts, migrate_product_contexts, seed_locations, slugify


CATEGORY_MAP = {
    "fresh produce": "Fruta",
    "bakery": "Padaria",
    "dairy & eggs": "Laticínios",
    "dairy and eggs": "Laticínios",
    "meat & fish": "Carne",
    "meat and fish": "Carne",
    "frozen": "Congelados",
    "pantry": "Mercearia",
    "household": "Limpeza",
    "groceries": "Mercearia",
    "electronics": "Vários",
}

CATEGORY_ORDER = [
    "Mercearia",
    "Fruta",
    "Legumes",
    "Laticínios",
    "Charcutaria",
    "Carne",
    "Peixe",
    "Carne e Peixe",
    "Congelados",
    "Padaria",
    "Bebidas",
    "Limpeza",
    "Higiene",
    "Vários",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_text(value: str, fallback: str) -> str:
    cleaned = (value or "").strip()
    return cleaned or fallback


def normalize_name(value: str) -> str:
    return (value or "").strip()


def canonicalize_category(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        return "Vários"
    mapped = CATEGORY_MAP.get(cleaned.lower())
    return mapped or cleaned


def _table_exists(connection, name: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (name,),
    ).fetchone()
    return row is not None


def _column_exists(connection, table: str, column: str) -> bool:
    rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row["name"] == column for row in rows)


@dataclass
class ListPayload:
    name: str
    store_name: str = ""
    budget: float = 0
    notes: str = ""


@dataclass
class ItemPayload:
    name: str
    quantity: float = 1
    unit: str = "unit"
    category: str = "Mercearia"
    aisle: str = "General"
    estimated_price: float = 0
    priority: int = 2
    note: str = ""


@dataclass
class ProductPayload:
    name: str
    category: str = "Vários"
    subcategory: str = ""
    default_unit: str = "un"
    default_quantity: float = 1
    default_estimated_price: float = 0
    default_priority: int = 2
    notes: str = ""


class ShoppingService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def bootstrap(self, categories: list[dict], templates: list[dict]) -> None:
        self.database.initialize()
        with self.database.connect() as connection:
            self._migrate_catalog(connection, templates)
            seed_locations(connection, utc_now())
            migrate_product_contexts(connection)
            total = connection.execute("SELECT COUNT(*) AS total FROM shopping_lists").fetchone()["total"]
            if total == 0:
                now = utc_now()
                connection.execute(
                    """
                    INSERT INTO shopping_lists (name, store_name, budget, notes, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 'active', ?, ?)
                    """,
                    ("Weekly Essentials", "My Supermarket", 80, "Use this as your fast-start list.", now, now),
                )

            active_list_id = self._get_default_list_id(connection)
            item_total = connection.execute(
                "SELECT COUNT(*) AS total FROM shopping_items WHERE list_id = ?",
                (active_list_id,),
            ).fetchone()["total"]
            if item_total == 0:
                for position, template in enumerate(templates[:5], start=1):
                    product_id = self._ensure_product(
                        connection,
                        name=template["name"],
                        category=template.get("category", "Mercearia"),
                        unit=template.get("unit", "un"),
                        quantity=float(template.get("quantity", 1) or 1),
                    )
                    self._insert_item(
                        connection,
                        active_list_id,
                        self._coerce_item(template),
                        position,
                        product_id,
                        increment_usage=True,
                    )

    def dashboard(self) -> dict[str, Any]:
        lists = self.list_lists()
        active_list_id = lists[0]["id"] if lists else None
        today = None
        if active_list_id:
            today = {
                "item_count": lists[0]["item_count"] or 0,
                "pending_count": lists[0]["pending_count"],
                "in_cart_count": lists[0]["in_cart_count"],
                "purchased_count": lists[0]["purchased_count"],
            }
        return {
            "lists": lists,
            "active_list_id": active_list_id,
            "suggestions": self.suggestions(),
            "product_count": self.product_count(active_only=True),
            "today": today,
            "locations": self.location_counts(),
        }

    def product_count(self, active_only: bool = True) -> int:
        with self.database.connect() as connection:
            if active_only:
                row = connection.execute(
                    "SELECT COUNT(*) AS total FROM products WHERE is_active = 1"
                ).fetchone()
            else:
                row = connection.execute("SELECT COUNT(*) AS total FROM products").fetchone()
        return int(row["total"])

    def list_products(self, query: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
        query = query or {}
        search = (query.get("search") or [""])[0].strip()
        category = (query.get("category") or [""])[0].strip()
        active_raw = (query.get("active") or ["1"])[0].strip().lower()

        clauses = []
        params: list[Any] = []
        if active_raw not in {"all", "*", ""}:
            if active_raw in {"0", "false", "inactive"}:
                clauses.append("is_active = 0")
            else:
                clauses.append("is_active = 1")
        if category:
            clauses.append("category = ?")
            params.append(category)
        if search:
            like = f"%{search}%"
            clauses.append("(name LIKE ? OR category LIKE ? OR subcategory LIKE ?)")
            params.extend([like, like, like])

        with self.database.connect() as connection:
            scoped_ids = self._product_ids_for_context(connection, query)
            if scoped_ids is not None:
                if not scoped_ids:
                    return []
                placeholders = ",".join("?" * len(scoped_ids))
                clauses.append(f"id IN ({placeholders})")
                params.extend(scoped_ids)

            where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
            sql = f"""
                SELECT *
                FROM products
                {where}
                ORDER BY
                    CASE category
                        {' '.join(f"WHEN ? THEN {index}" for index, _ in enumerate(CATEGORY_ORDER))}
                        ELSE {len(CATEGORY_ORDER)}
                    END,
                    name COLLATE NOCASE ASC
            """
            params = [*params, *CATEGORY_ORDER]
            rows = connection.execute(sql, params).fetchall()
            products = [self._serialize_product(row) for row in rows]
            return attach_product_contexts(connection, products)

    def create_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = self._coerce_product(payload)
        created = True
        with self.database.connect() as connection:
            existing = self._find_product_row(connection, data.name)
            if existing is not None:
                created = False
                product_id = int(existing["id"])
                if not existing["is_active"]:
                    connection.execute(
                        "UPDATE products SET is_active = 1, updated_at = ? WHERE id = ?",
                        (utc_now(), product_id),
                    )
            else:
                product_id = self._insert_product(connection, data)
            self._sync_product_types(connection, product_id, payload, replace=False)
        product = self.get_product(product_id)
        product["_created"] = created
        return product

    def get_product(self, product_id: int) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if row is None:
                raise KeyError("Product not found")
            return attach_product_contexts(connection, [self._serialize_product(row)])[0]

    def update_product(self, product_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        current = self.get_product(product_id)
        merged = {**current, **payload}
        data = self._coerce_product(merged)
        now = utc_now()
        is_active = current["is_active"]
        if "is_active" in payload:
            is_active = 1 if payload.get("is_active") else 0
        with self.database.connect() as connection:
            other = self._find_product_row(connection, data.name)
            if other is not None and int(other["id"]) != product_id:
                raise ValueError("Já existe um produto com este nome")
            connection.execute(
                """
                UPDATE products
                SET name = ?, category = ?, subcategory = ?, default_unit = ?, default_quantity = ?,
                    default_estimated_price = ?, default_priority = ?, notes = ?, is_active = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    data.name,
                    data.category,
                    data.subcategory,
                    data.default_unit,
                    data.default_quantity,
                    data.default_estimated_price,
                    data.default_priority,
                    data.notes,
                    is_active,
                    now,
                    product_id,
                ),
            )
            self._sync_product_types(connection, product_id, payload, replace=True)
        return self.get_product(product_id)

    def deactivate_product(self, product_id: int) -> dict[str, Any]:
        self.get_product(product_id)
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE products SET is_active = 0, updated_at = ? WHERE id = ?",
                (utc_now(), product_id),
            )
        return self.get_product(product_id)

    def add_product_to_list(self, list_id: int, product_id: int, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        self.get_list(list_id)
        product = self.get_product(product_id)
        payload = payload or {}
        item_payload = {
            "name": product["name"],
            "quantity": payload.get("quantity", product["default_quantity"]),
            "unit": payload.get("unit") or product["default_unit"],
            "category": product["category"],
            "aisle": payload.get("aisle") or "Geral",
            "estimated_price": payload.get("estimated_price", product["default_estimated_price"]),
            "priority": payload.get("priority", product["default_priority"]),
            "note": payload.get("note", ""),
        }
        return self.create_item(list_id, item_payload)

    def list_lists(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    l.*,
                    COUNT(i.id) AS item_count,
                    SUM(CASE WHEN i.status = 'purchased' THEN 1 ELSE 0 END) AS purchased_count,
                    SUM(CASE WHEN i.status = 'pending' THEN 1 ELSE 0 END) AS pending_count,
                    SUM(CASE WHEN i.status = 'in_cart' THEN 1 ELSE 0 END) AS in_cart_count,
                    COALESCE(SUM(i.estimated_price * i.quantity), 0) AS estimated_total
                FROM shopping_lists l
                LEFT JOIN shopping_items i ON i.list_id = l.id
                GROUP BY l.id
                ORDER BY CASE l.status WHEN 'active' THEN 0 ELSE 1 END, l.updated_at DESC
                """
            ).fetchall()
        return [self._serialize_list(row) for row in rows]

    def create_list(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = ListPayload(
            name=normalize_text(payload.get("name", ""), "New Shopping Trip"),
            store_name=normalize_text(payload.get("store_name", ""), ""),
            budget=float(payload.get("budget", 0) or 0),
            notes=(payload.get("notes") or "").strip(),
        )
        now = utc_now()
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO shopping_lists (name, store_name, budget, notes, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'active', ?, ?)
                """,
                (data.name, data.store_name, data.budget, data.notes, now, now),
            )
            list_id = cursor.lastrowid
        return self.get_list(list_id)

    def get_list(self, list_id: int) -> dict[str, Any]:
        with self.database.connect() as connection:
            list_row = connection.execute(
                """
                SELECT
                    l.*,
                    COUNT(i.id) AS item_count,
                    SUM(CASE WHEN i.status = 'purchased' THEN 1 ELSE 0 END) AS purchased_count,
                    SUM(CASE WHEN i.status = 'pending' THEN 1 ELSE 0 END) AS pending_count,
                    SUM(CASE WHEN i.status = 'in_cart' THEN 1 ELSE 0 END) AS in_cart_count,
                    COALESCE(SUM(i.estimated_price * i.quantity), 0) AS estimated_total
                FROM shopping_lists l
                LEFT JOIN shopping_items i ON i.list_id = l.id
                WHERE l.id = ?
                GROUP BY l.id
                """,
                (list_id,),
            ).fetchone()
            if list_row is None:
                raise KeyError("List not found")
            category_case = " ".join(
                f"WHEN ? THEN {index}" for index, _ in enumerate(CATEGORY_ORDER)
            )
            item_rows = connection.execute(
                f"""
                SELECT *
                FROM shopping_items
                WHERE list_id = ?
                ORDER BY
                    CASE status WHEN 'pending' THEN 0 WHEN 'in_cart' THEN 1 ELSE 2 END,
                    CASE category
                        {category_case}
                        ELSE {len(CATEGORY_ORDER)}
                    END,
                    aisle ASC,
                    priority ASC,
                    position ASC,
                    name COLLATE NOCASE ASC
                """,
                (list_id, *CATEGORY_ORDER),
            ).fetchall()
        data = self._serialize_list(list_row)
        data["items"] = [self._serialize_item(row) for row in item_rows]
        data["summary"] = self._summarize_items(data["items"], data["budget"])
        return data

    def update_list(self, list_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        current = self.get_list(list_id)
        now = utc_now()
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE shopping_lists
                SET name = ?, store_name = ?, budget = ?, notes = ?, status = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    normalize_text(payload.get("name", current["name"]), "New Shopping Trip"),
                    normalize_text(payload.get("store_name", current["store_name"]), ""),
                    float(payload.get("budget", current["budget"]) or 0),
                    (payload.get("notes", current["notes"]) or "").strip(),
                    payload.get("status", current["status"]),
                    now,
                    list_id,
                ),
            )
        return self.get_list(list_id)

    def duplicate_list(self, list_id: int) -> dict[str, Any]:
        source = self.get_list(list_id)
        clone = self.create_list(
            {
                "name": f"{source['name']} Copy",
                "store_name": source["store_name"],
                "budget": source["budget"],
                "notes": source["notes"],
            }
        )
        for item in source["items"]:
            self.create_item(clone["id"], item)
        return self.get_list(clone["id"])

    def delete_list(self, list_id: int) -> None:
        with self.database.connect() as connection:
            connection.execute("DELETE FROM shopping_lists WHERE id = ?", (list_id,))

    def create_item(self, list_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        data = self._coerce_item(payload)
        merged = False
        with self.database.connect() as connection:
            product_id = self._ensure_product(
                connection,
                name=data.name,
                category=data.category,
                unit=data.unit,
                quantity=data.quantity,
                estimated_price=data.estimated_price,
                priority=data.priority,
                notes=data.note,
            )
            product = connection.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            canonical = ItemPayload(
                name=product["name"],
                quantity=data.quantity,
                unit=data.unit or product["default_unit"],
                category=product["category"],
                aisle=data.aisle,
                estimated_price=data.estimated_price,
                priority=data.priority,
                note=data.note,
            )
            existing = connection.execute(
                """
                SELECT id, quantity FROM shopping_items
                WHERE list_id = ? AND product_id = ?
                """,
                (list_id, product_id),
            ).fetchone()
            now = utc_now()
            if existing is not None:
                connection.execute(
                    """
                    UPDATE shopping_items
                    SET quantity = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (float(existing["quantity"]) + canonical.quantity, now, existing["id"]),
                )
                connection.execute("UPDATE shopping_lists SET updated_at = ? WHERE id = ?", (now, list_id))
                item_id = int(existing["id"])
                merged = True
            else:
                position = connection.execute(
                    "SELECT COALESCE(MAX(position), 0) + 1 AS next_position FROM shopping_items WHERE list_id = ?",
                    (list_id,),
                ).fetchone()["next_position"]
                item_id = self._insert_item(connection, list_id, canonical, position, product_id, increment_usage=True)
                connection.execute("UPDATE shopping_lists SET updated_at = ? WHERE id = ?", (now, list_id))
        item = self.get_item(item_id)
        item["merged"] = merged
        return item

    def get_item(self, item_id: int) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM shopping_items WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            raise KeyError("Item not found")
        return self._serialize_item(row)

    def update_item(self, item_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        current = self.get_item(item_id)
        merged = {**current, **payload}
        data = self._coerce_item(merged)
        status = payload.get("status", current["status"])
        now = utc_now()
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE shopping_items
                SET name = ?, quantity = ?, unit = ?, category = ?, aisle = ?, estimated_price = ?,
                    priority = ?, note = ?, status = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    data.name,
                    data.quantity,
                    data.unit,
                    data.category,
                    data.aisle,
                    data.estimated_price,
                    data.priority,
                    data.note,
                    status,
                    now,
                    item_id,
                ),
            )
            connection.execute("UPDATE shopping_lists SET updated_at = ? WHERE id = ?", (now, current["list_id"]))
        return self.get_item(item_id)

    def cycle_item_status(self, item_id: int) -> dict[str, Any]:
        current = self.get_item(item_id)
        next_status = {"pending": "in_cart", "in_cart": "purchased", "purchased": "pending"}[current["status"]]
        return self.update_item(item_id, {"status": next_status})

    def delete_item(self, item_id: int) -> None:
        item = self.get_item(item_id)
        with self.database.connect() as connection:
            connection.execute("DELETE FROM shopping_items WHERE id = ?", (item_id,))
            connection.execute("UPDATE shopping_lists SET updated_at = ? WHERE id = ?", (utc_now(), item["list_id"]))

    def suggestions(self, limit: int = 12) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    name,
                    category,
                    subcategory,
                    default_unit AS unit,
                    default_quantity,
                    times_used,
                    last_used_at
                FROM products
                WHERE is_active = 1
                ORDER BY times_used DESC, last_used_at DESC, name COLLATE NOCASE ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def location_counts(self) -> dict[str, int]:
        with self.database.connect() as connection:
            types = connection.execute(
                "SELECT COUNT(*) AS total FROM commerce_types WHERE is_active = 1"
            ).fetchone()["total"]
            stores = connection.execute(
                "SELECT COUNT(*) AS total FROM stores WHERE is_active = 1"
            ).fetchone()["total"]
        return {"commerce_type_count": int(types), "store_count": int(stores)}

    def list_commerce_types(self, query: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
        query = query or {}
        active_raw = (query.get("active") or ["1"])[0].strip().lower()
        clauses = []
        if active_raw not in {"all", "*", ""}:
            clauses.append("is_active = 0" if active_raw in {"0", "false", "inactive"} else "is_active = 1")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.database.connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM commerce_types {where} ORDER BY position ASC, name COLLATE NOCASE ASC"
            ).fetchall()
        return [self._serialize_flag_row(row) for row in rows]

    def create_commerce_type(self, payload: dict[str, Any]) -> dict[str, Any]:
        name = normalize_name(payload.get("name", ""))
        if not name:
            raise ValueError("O nome do tipo de comércio é obrigatório")
        slug = slugify(payload.get("slug") or name)
        now = utc_now()
        with self.database.connect() as connection:
            existing = connection.execute("SELECT * FROM commerce_types WHERE slug = ?", (slug,)).fetchone()
            if existing is not None:
                return self._serialize_flag_row(existing)
            position = connection.execute(
                "SELECT COALESCE(MAX(position), 0) + 1 AS next_position FROM commerce_types"
            ).fetchone()["next_position"]
            cursor = connection.execute(
                """
                INSERT INTO commerce_types (name, slug, description, icon, position, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    name,
                    slug,
                    (payload.get("description") or "").strip(),
                    (payload.get("icon") or "").strip(),
                    int(payload.get("position") or position),
                    now,
                    now,
                ),
            )
            type_id = cursor.lastrowid
        return self.get_commerce_type(type_id)

    def get_commerce_type(self, type_id: int) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM commerce_types WHERE id = ?", (type_id,)).fetchone()
        if row is None:
            raise KeyError("Commerce type not found")
        return self._serialize_flag_row(row)

    def update_commerce_type(self, type_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        current = self.get_commerce_type(type_id)
        name = normalize_name(payload.get("name", current["name"])) or current["name"]
        now = utc_now()
        is_active = current["is_active"] if "is_active" not in payload else bool(payload.get("is_active"))
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE commerce_types
                SET name = ?, description = ?, icon = ?, position = ?, is_active = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    name,
                    (payload.get("description", current["description"]) or "").strip(),
                    (payload.get("icon", current["icon"]) or "").strip(),
                    int(payload.get("position", current["position"]) or 0),
                    1 if is_active else 0,
                    now,
                    type_id,
                ),
            )
        return self.get_commerce_type(type_id)

    def deactivate_commerce_type(self, type_id: int) -> dict[str, Any]:
        return self.update_commerce_type(type_id, {"is_active": False})

    def list_stores(self, query: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
        query = query or {}
        search = (query.get("search") or [""])[0].strip()
        type_raw = (query.get("commerce_type_id") or [""])[0].strip()
        active_raw = (query.get("active") or ["1"])[0].strip().lower()
        clauses = []
        params: list[Any] = []
        if active_raw not in {"all", "*", ""}:
            clauses.append("s.is_active = 0" if active_raw in {"0", "false", "inactive"} else "s.is_active = 1")
        if type_raw:
            clauses.append("s.commerce_type_id = ?")
            params.append(int(type_raw))
        if search:
            clauses.append("s.name LIKE ?")
            params.append(f"%{search}%")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.database.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT s.*, c.name AS commerce_type_name, c.slug AS commerce_type_slug
                FROM stores s
                JOIN commerce_types c ON c.id = s.commerce_type_id
                {where}
                ORDER BY c.position ASC, s.name COLLATE NOCASE ASC
                """,
                params,
            ).fetchall()
        return [self._serialize_store(row) for row in rows]

    def create_store(self, payload: dict[str, Any]) -> dict[str, Any]:
        name = normalize_name(payload.get("name", ""))
        if not name:
            raise ValueError("O nome da loja é obrigatório")
        type_id = int(payload.get("commerce_type_id") or 0)
        self.get_commerce_type(type_id)
        slug = slugify(payload.get("slug") or name)
        now = utc_now()
        with self.database.connect() as connection:
            existing = connection.execute("SELECT id FROM stores WHERE slug = ?", (slug,)).fetchone()
            if existing is not None:
                return self.get_store(int(existing["id"]))
            cursor = connection.execute(
                """
                INSERT INTO stores (name, commerce_type_id, slug, notes, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, ?, ?)
                """,
                (name, type_id, slug, (payload.get("notes") or "").strip(), now, now),
            )
            store_id = cursor.lastrowid
        return self.get_store(store_id)

    def get_store(self, store_id: int) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT s.*, c.name AS commerce_type_name, c.slug AS commerce_type_slug
                FROM stores s
                JOIN commerce_types c ON c.id = s.commerce_type_id
                WHERE s.id = ?
                """,
                (store_id,),
            ).fetchone()
        if row is None:
            raise KeyError("Store not found")
        return self._serialize_store(row)

    def update_store(self, store_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        current = self.get_store(store_id)
        name = normalize_name(payload.get("name", current["name"])) or current["name"]
        type_id = int(payload.get("commerce_type_id", current["commerce_type_id"]))
        self.get_commerce_type(type_id)
        is_active = current["is_active"] if "is_active" not in payload else bool(payload.get("is_active"))
        now = utc_now()
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE stores
                SET name = ?, commerce_type_id = ?, notes = ?, is_active = ?, updated_at = ?
                WHERE id = ?
                """,
                (name, type_id, (payload.get("notes", current["notes"]) or "").strip(), 1 if is_active else 0, now, store_id),
            )
        return self.get_store(store_id)

    def deactivate_store(self, store_id: int) -> dict[str, Any]:
        return self.update_store(store_id, {"is_active": False})

    def add_product_commerce_type(self, product_id: int, type_id: int) -> dict[str, Any]:
        self.get_product(product_id)
        self.get_commerce_type(type_id)
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO product_commerce_types (product_id, commerce_type_id, priority)
                VALUES (?, ?, 0)
                """,
                (product_id, type_id),
            )
        return self.get_product(product_id)

    def remove_product_commerce_type(self, product_id: int, type_id: int) -> dict[str, Any]:
        self.get_product(product_id)
        with self.database.connect() as connection:
            connection.execute(
                "DELETE FROM product_commerce_types WHERE product_id = ? AND commerce_type_id = ?",
                (product_id, type_id),
            )
        return self.get_product(product_id)

    def add_product_store(self, product_id: int, store_id: int) -> dict[str, Any]:
        self.get_product(product_id)
        self.get_store(store_id)
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO product_stores (product_id, store_id, priority)
                VALUES (?, ?, 0)
                """,
                (product_id, store_id),
            )
        return self.get_product(product_id)

    def remove_product_store(self, product_id: int, store_id: int) -> dict[str, Any]:
        self.get_product(product_id)
        with self.database.connect() as connection:
            connection.execute(
                "DELETE FROM product_stores WHERE product_id = ? AND store_id = ?",
                (product_id, store_id),
            )
        return self.get_product(product_id)

    def _product_ids_for_context(self, connection, query: dict[str, list[str]]) -> list[int] | None:
        store_raw = (query.get("store_id") or [""])[0].strip()
        type_raw = (query.get("commerce_type_id") or [""])[0].strip()
        if store_raw:
            store_id = int(store_raw)
            store = connection.execute("SELECT * FROM stores WHERE id = ?", (store_id,)).fetchone()
            if store is None:
                return []
            rows = connection.execute(
                """
                SELECT product_id FROM product_stores WHERE store_id = ?
                UNION
                SELECT product_id FROM product_commerce_types WHERE commerce_type_id = ?
                """,
                (store_id, store["commerce_type_id"]),
            ).fetchall()
            return [int(row["product_id"]) for row in rows]
        if type_raw:
            type_id = int(type_raw)
            rows = connection.execute(
                "SELECT product_id FROM product_commerce_types WHERE commerce_type_id = ?",
                (type_id,),
            ).fetchall()
            return [int(row["product_id"]) for row in rows]
        return None

    def _sync_product_types(self, connection, product_id: int, payload: dict[str, Any], replace: bool) -> None:
        if "commerce_type_ids" not in payload:
            return
        raw_ids = payload.get("commerce_type_ids") or []
        type_ids: list[int] = []
        for value in raw_ids:
            try:
                type_ids.append(int(value))
            except (TypeError, ValueError):
                continue
        type_ids = list(dict.fromkeys(type_ids))
        if replace:
            connection.execute("DELETE FROM product_commerce_types WHERE product_id = ?", (product_id,))
        for type_id in type_ids:
            exists = connection.execute("SELECT id FROM commerce_types WHERE id = ?", (type_id,)).fetchone()
            if exists is None:
                continue
            connection.execute(
                """
                INSERT OR IGNORE INTO product_commerce_types (product_id, commerce_type_id, priority)
                VALUES (?, ?, 0)
                """,
                (product_id, type_id),
            )

    def _migrate_catalog(self, connection, templates: list[dict]) -> None:
        if _table_exists(connection, "item_templates"):
            templates_rows = connection.execute(
                """
                SELECT name, category, aisle, unit, default_quantity, times_used, last_used_at
                FROM item_templates
                ORDER BY id ASC
                """
            ).fetchall()
            for row in templates_rows:
                self._ensure_product(
                    connection,
                    name=row["name"],
                    category=row["category"],
                    unit=row["unit"],
                    quantity=float(row["default_quantity"] or 1),
                    times_used=int(row["times_used"] or 0),
                    last_used_at=row["last_used_at"],
                    reactivate=False,
                )

        for template in templates:
            self._ensure_product(
                connection,
                name=template["name"],
                category=template.get("category", "Mercearia"),
                unit=template.get("unit", "un"),
                quantity=float(template.get("quantity", 1) or 1),
                reactivate=False,
            )

        if _column_exists(connection, "shopping_items", "product_id"):
            items = connection.execute(
                "SELECT id, name, category, unit, quantity, estimated_price, priority, note, product_id FROM shopping_items"
            ).fetchall()
            for item in items:
                if item["product_id"]:
                    continue
                product_id = self._ensure_product(
                    connection,
                    name=item["name"],
                    category=item["category"],
                    unit=item["unit"],
                    quantity=float(item["quantity"] or 1),
                    estimated_price=float(item["estimated_price"] or 0),
                    priority=int(item["priority"] or 2),
                    notes=item["note"] or "",
                    reactivate=False,
                )
                connection.execute(
                    "UPDATE shopping_items SET product_id = ? WHERE id = ?",
                    (product_id, item["id"]),
                )

            connection.execute(
                """
                UPDATE shopping_items
                SET category = (
                    SELECT category FROM products WHERE products.id = shopping_items.product_id
                )
                WHERE product_id IS NOT NULL
                """
            )

    def _find_product_row(self, connection, name: str):
        cleaned = normalize_name(name)
        if not cleaned:
            return None
        return connection.execute(
            "SELECT * FROM products WHERE lower(name) = lower(?) LIMIT 1",
            (cleaned,),
        ).fetchone()

    def _ensure_product(
        self,
        connection,
        *,
        name: str,
        category: str = "Vários",
        unit: str = "un",
        quantity: float = 1,
        estimated_price: float = 0,
        priority: int = 2,
        notes: str = "",
        times_used: int | None = None,
        last_used_at: str | None = None,
        reactivate: bool = True,
    ) -> int:
        cleaned = normalize_name(name) or "Novo produto"
        existing = self._find_product_row(connection, cleaned)
        now = utc_now()
        if existing is not None:
            if reactivate and not existing["is_active"]:
                connection.execute(
                    "UPDATE products SET is_active = 1, updated_at = ? WHERE id = ?",
                    (now, existing["id"]),
                )
            return int(existing["id"])

        payload = ProductPayload(
            name=cleaned,
            category=canonicalize_category(category),
            default_unit=normalize_text(unit, "un"),
            default_quantity=float(quantity or 1),
            default_estimated_price=float(estimated_price or 0),
            default_priority=min(max(int(priority or 2), 1), 3),
            notes=(notes or "").strip(),
        )
        used = 0 if times_used is None else int(times_used)
        cursor = connection.execute(
            """
            INSERT INTO products (
                name, category, subcategory, default_unit, default_quantity, default_estimated_price,
                default_priority, notes, is_active, created_at, updated_at, last_used_at, times_used
            )
            VALUES (?, ?, '', ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
            """,
            (
                payload.name,
                payload.category,
                payload.default_unit,
                payload.default_quantity,
                payload.default_estimated_price,
                payload.default_priority,
                payload.notes,
                now,
                now,
                last_used_at,
                used,
            ),
        )
        return int(cursor.lastrowid)

    def _insert_product(self, connection, data: ProductPayload) -> int:
        now = utc_now()
        cursor = connection.execute(
            """
            INSERT INTO products (
                name, category, subcategory, default_unit, default_quantity, default_estimated_price,
                default_priority, notes, is_active, created_at, updated_at, last_used_at, times_used
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, NULL, 0)
            """,
            (
                data.name,
                data.category,
                data.subcategory,
                data.default_unit,
                data.default_quantity,
                data.default_estimated_price,
                data.default_priority,
                data.notes,
                now,
                now,
            ),
        )
        return int(cursor.lastrowid)

    def _register_product_use(self, connection, product_id: int) -> None:
        now = utc_now()
        connection.execute(
            """
            UPDATE products
            SET times_used = times_used + 1, last_used_at = ?, updated_at = ?, is_active = 1
            WHERE id = ?
            """,
            (now, now, product_id),
        )

    def _coerce_item(self, payload: dict[str, Any]) -> ItemPayload:
        quantity = float(payload.get("quantity", 1) or 1)
        estimated_price = float(payload.get("estimated_price", 0) or 0)
        priority = int(payload.get("priority", 2) or 2)
        priority = min(max(priority, 1), 3)
        return ItemPayload(
            name=normalize_name(payload.get("name", "")) or "Novo produto",
            quantity=quantity,
            unit=normalize_text(payload.get("unit", ""), "un"),
            category=canonicalize_category(payload.get("category", "")),
            aisle=normalize_text(payload.get("aisle", ""), "Geral"),
            estimated_price=estimated_price,
            priority=priority,
            note=(payload.get("note") or "").strip(),
        )

    def _coerce_product(self, payload: dict[str, Any]) -> ProductPayload:
        name = normalize_name(payload.get("name", ""))
        if not name:
            raise ValueError("O nome do produto é obrigatório")
        quantity = float(payload.get("default_quantity", payload.get("quantity", 1)) or 1)
        price = float(payload.get("default_estimated_price", payload.get("estimated_price", 0)) or 0)
        priority = int(payload.get("default_priority", payload.get("priority", 2)) or 2)
        return ProductPayload(
            name=name,
            category=canonicalize_category(payload.get("category", "")),
            subcategory=(payload.get("subcategory") or "").strip(),
            default_unit=normalize_text(
                payload.get("default_unit", payload.get("unit", "")),
                "un",
            ),
            default_quantity=quantity,
            default_estimated_price=price,
            default_priority=min(max(priority, 1), 3),
            notes=(payload.get("notes") or payload.get("note") or "").strip(),
        )

    def _get_default_list_id(self, connection) -> int:
        row = connection.execute(
            "SELECT id FROM shopping_lists ORDER BY CASE status WHEN 'active' THEN 0 ELSE 1 END, updated_at DESC LIMIT 1"
        ).fetchone()
        return int(row["id"])

    def _insert_item(
        self,
        connection,
        list_id: int,
        payload: ItemPayload,
        position: int,
        product_id: int,
        increment_usage: bool = False,
    ) -> int:
        now = utc_now()
        cursor = connection.execute(
            """
            INSERT INTO shopping_items (
                list_id, product_id, name, quantity, unit, category, aisle, estimated_price, priority, note,
                status, position, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)
            """,
            (
                list_id,
                product_id,
                payload.name,
                payload.quantity,
                payload.unit,
                payload.category,
                payload.aisle,
                payload.estimated_price,
                payload.priority,
                payload.note,
                position,
                now,
                now,
            ),
        )
        if increment_usage:
            self._register_product_use(connection, product_id)
        return int(cursor.lastrowid)

    def _serialize_list(self, row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "name": row["name"],
            "store_name": row["store_name"],
            "budget": row["budget"],
            "notes": row["notes"],
            "status": row["status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "item_count": row["item_count"] or 0,
            "purchased_count": row["purchased_count"] or 0,
            "pending_count": (row["pending_count"] if "pending_count" in row.keys() else 0) or 0,
            "in_cart_count": (row["in_cart_count"] if "in_cart_count" in row.keys() else 0) or 0,
            "estimated_total": round(row["estimated_total"] or 0, 2),
        }

    def _serialize_item(self, row) -> dict[str, Any]:
        data = dict(row)
        data["line_total"] = round(data["quantity"] * data["estimated_price"], 2)
        return data

    def _serialize_product(self, row) -> dict[str, Any]:
        data = dict(row)
        data["is_active"] = bool(data["is_active"])
        return data

    def _serialize_flag_row(self, row) -> dict[str, Any]:
        data = dict(row)
        data["is_active"] = bool(data["is_active"])
        return data

    def _serialize_store(self, row) -> dict[str, Any]:
        data = self._serialize_flag_row(row)
        return data

    def _summarize_items(self, items: list[dict[str, Any]], budget: float) -> dict[str, Any]:
        total = round(sum(item["line_total"] for item in items), 2)
        purchased = sum(1 for item in items if item["status"] == "purchased")
        in_cart = sum(1 for item in items if item["status"] == "in_cart")
        pending = sum(1 for item in items if item["status"] == "pending")
        return {
            "estimated_total": total,
            "budget_remaining": round(budget - total, 2),
            "purchased_count": purchased,
            "in_cart_count": in_cart,
            "pending_count": pending,
            "aisles": sorted({item["aisle"] for item in items}),
            "completion_rate": round((purchased / len(items)) * 100, 1) if items else 0,
        }
