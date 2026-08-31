import sqlite3
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


def optional_money(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        cleaned = value.strip().replace(" ", "").replace(",", ".")
        if cleaned == "":
            return None
        value = cleaned
    return round(float(value), 2)


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
        active = next((row for row in lists if row["status"] == "active"), None)
        active_list_id = active["id"] if active else None
        today = None
        if active:
            today = {
                "item_count": active["item_count"] or 0,
                "pending_count": active["pending_count"],
                "in_cart_count": active["in_cart_count"],
                "purchased_count": active["purchased_count"],
                "commerce_type_id": active.get("commerce_type_id"),
                "store_id": active.get("store_id"),
                "commerce_type_name": active.get("commerce_type_name"),
                "location_store_name": active.get("location_store_name"),
                "location_label": active.get("location_label"),
                "location_short": active.get("location_short"),
            }
        return {
            "lists": lists,
            "active_list_id": active_list_id,
            "suggestions": self.suggestions(),
            "product_count": self.product_count(active_only=True),
            "today": today,
            "locations": self.location_counts(),
            "history": self.history_summary(),
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
            products = attach_product_contexts(connection, [self._serialize_product(row) for row in rows])
            self._attach_product_insights(connection, products)
            return products

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
            self._sync_product_stores(connection, product_id, payload, replace=False)
        product = self.get_product(product_id)
        product["_created"] = created
        return product

    def get_product(self, product_id: int) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if row is None:
                raise KeyError("Product not found")
            products = attach_product_contexts(connection, [self._serialize_product(row)])
            self._attach_product_insights(connection, products)
            return products[0]

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
            self._sync_product_stores(connection, product_id, payload, replace=True)
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
                    c.name AS commerce_type_name,
                    s.name AS location_store_name,
                    COUNT(i.id) AS item_count,
                    SUM(CASE WHEN i.status = 'purchased' THEN 1 ELSE 0 END) AS purchased_count,
                    SUM(CASE WHEN i.status = 'pending' THEN 1 ELSE 0 END) AS pending_count,
                    SUM(CASE WHEN i.status = 'in_cart' THEN 1 ELSE 0 END) AS in_cart_count,
                    COALESCE(SUM(i.estimated_price * i.quantity), 0) AS estimated_total,
                    (
                        SELECT h.id FROM purchase_history h
                        WHERE h.source_list_id = l.id
                        LIMIT 1
                    ) AS history_id
                FROM shopping_lists l
                LEFT JOIN commerce_types c ON c.id = l.commerce_type_id
                LEFT JOIN stores s ON s.id = l.store_id
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
        type_id, store_id = self._normalize_list_context(payload)
        now = utc_now()
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO shopping_lists (
                    name, store_name, budget, notes, status, commerce_type_id, store_id, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, 'active', ?, ?, ?, ?)
                """,
                (data.name, data.store_name, data.budget, data.notes, type_id, store_id, now, now),
            )
            list_id = cursor.lastrowid
        return self.get_list(list_id)

    def get_list(self, list_id: int) -> dict[str, Any]:
        with self.database.connect() as connection:
            list_row = connection.execute(
                """
                SELECT
                    l.*,
                    c.name AS commerce_type_name,
                    s.name AS location_store_name,
                    COUNT(i.id) AS item_count,
                    SUM(CASE WHEN i.status = 'purchased' THEN 1 ELSE 0 END) AS purchased_count,
                    SUM(CASE WHEN i.status = 'pending' THEN 1 ELSE 0 END) AS pending_count,
                    SUM(CASE WHEN i.status = 'in_cart' THEN 1 ELSE 0 END) AS in_cart_count,
                    COALESCE(SUM(i.estimated_price * i.quantity), 0) AS estimated_total,
                    (
                        SELECT h.id FROM purchase_history h
                        WHERE h.source_list_id = l.id
                        LIMIT 1
                    ) AS history_id
                FROM shopping_lists l
                LEFT JOIN commerce_types c ON c.id = l.commerce_type_id
                LEFT JOIN stores s ON s.id = l.store_id
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
            self._attach_item_context_flags(connection, data["items"], data)
            data["summary"] = self._summarize_items(data["items"], data["budget"])
        return data

    def update_list(self, list_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        current = self.get_list(list_id)
        type_id, store_id = self._normalize_list_context(payload, current)
        now = utc_now()
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE shopping_lists
                SET name = ?, store_name = ?, budget = ?, notes = ?, status = ?,
                    commerce_type_id = ?, store_id = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    normalize_text(payload.get("name", current["name"]), "New Shopping Trip"),
                    normalize_text(payload.get("store_name", current["store_name"]), ""),
                    float(payload.get("budget", current["budget"]) or 0),
                    (payload.get("notes", current["notes"]) or "").strip(),
                    payload.get("status", current["status"]),
                    type_id,
                    store_id,
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
                "commerce_type_id": source.get("commerce_type_id"),
                "store_id": source.get("store_id"),
            }
        )
        for item in source["items"]:
            self.create_item(clone["id"], item)
        return self.get_list(clone["id"])

    def delete_list(self, list_id: int) -> None:
        with self.database.connect() as connection:
            connection.execute("DELETE FROM shopping_lists WHERE id = ?", (list_id,))

    def history_summary(self) -> dict[str, Any]:
        with self.database.connect() as connection:
            if not _table_exists(connection, "purchase_history"):
                return {"count": 0, "last_completed_at": None, "last_store_name": ""}
            row = connection.execute(
                """
                SELECT
                    COUNT(*) AS count,
                    MAX(completed_at) AS last_completed_at
                FROM purchase_history
                """
            ).fetchone()
            latest = connection.execute(
                """
                SELECT store_name, commerce_type_name, store_id, commerce_type_id
                FROM purchase_history
                ORDER BY completed_at DESC, id DESC
                LIMIT 1
                """
            ).fetchone()
        return {
            "count": int(row["count"] or 0),
            "last_completed_at": row["last_completed_at"],
            "last_store_name": (latest["store_name"] if latest else "") or "",
            "last_commerce_type_name": (latest["commerce_type_name"] if latest else "") or "",
            "last_store_id": latest["store_id"] if latest else None,
            "last_commerce_type_id": latest["commerce_type_id"] if latest else None,
        }

    def complete_list(self, list_id: int) -> dict[str, Any]:
        with self.database.connect() as connection:
            existing = connection.execute(
                "SELECT id FROM purchase_history WHERE source_list_id = ?",
                (list_id,),
            ).fetchone()
            if existing is not None:
                return self._complete_payload(connection, int(existing["id"]))

            listed = self._list_row(connection, list_id)
            items = connection.execute(
                """
                SELECT *
                FROM shopping_items
                WHERE list_id = ?
                ORDER BY position ASC, id ASC
                """,
                (list_id,),
            ).fetchall()
            if not items:
                raise ValueError("A lista está vazia")

            now = utc_now()
            type_id = listed["commerce_type_id"]
            store_id = listed["store_id"]
            commerce_type_name = listed["commerce_type_name"] or ""
            store_name = listed["location_store_name"] or ""
            estimated_total = round(
                sum(float(item["quantity"] or 0) * float(item["estimated_price"] or 0) for item in items),
                2,
            )
            priced = 0
            unpriced = 0
            actual_total = 0.0
            snapshots = []
            for position, item in enumerate(items, start=1):
                snapshot = self._history_item_snapshot(connection, item, position, now)
                snapshots.append(snapshot)
                if snapshot["actual_unit_price"] is None:
                    unpriced += 1
                else:
                    priced += 1
                    actual_total += snapshot["actual_line_total"] or 0
            actual_total = round(actual_total, 2) if priced else None

            try:
                cursor = connection.execute(
                    """
                    INSERT INTO purchase_history (
                        source_list_id, name, completed_at, commerce_type_id, store_id,
                        commerce_type_name, store_name, estimated_total, actual_total, notes, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        list_id,
                        listed["name"],
                        now,
                        type_id,
                        store_id,
                        commerce_type_name,
                        store_name,
                        estimated_total,
                        actual_total,
                        listed["notes"] or "",
                        now,
                    ),
                )
                history_id = int(cursor.lastrowid)
            except sqlite3.IntegrityError:
                existing = connection.execute(
                    "SELECT id FROM purchase_history WHERE source_list_id = ?",
                    (list_id,),
                ).fetchone()
                if existing is None:
                    raise
                return self._complete_payload(connection, int(existing["id"]))

            for snapshot in snapshots:
                connection.execute(
                    """
                    INSERT INTO purchase_history_items (
                        purchase_history_id, product_id, product_name, category, subcategory,
                        quantity, unit, estimated_price, actual_unit_price, actual_line_total,
                        status, aisle, note, position, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        history_id,
                        snapshot["product_id"],
                        snapshot["product_name"],
                        snapshot["category"],
                        snapshot["subcategory"],
                        snapshot["quantity"],
                        snapshot["unit"],
                        snapshot["estimated_price"],
                        snapshot["actual_unit_price"],
                        snapshot["actual_line_total"],
                        snapshot["status"],
                        snapshot["aisle"],
                        snapshot["note"],
                        snapshot["position"],
                        now,
                    ),
                )

            connection.execute(
                "UPDATE shopping_lists SET status = 'archived', updated_at = ? WHERE id = ?",
                (now, list_id),
            )
            return self._complete_payload(connection, history_id)

    def list_history(self, query: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
        query = query or {}
        clauses: list[str] = []
        params: list[Any] = []
        store_raw = (query.get("store_id") or [""])[0].strip()
        type_raw = (query.get("commerce_type_id") or [""])[0].strip()
        from_raw = (query.get("from") or [""])[0].strip()
        to_raw = (query.get("to") or [""])[0].strip()
        if store_raw:
            clauses.append("h.store_id = ?")
            params.append(int(store_raw))
        if type_raw:
            clauses.append("h.commerce_type_id = ?")
            params.append(int(type_raw))
        if from_raw:
            clauses.append("h.completed_at >= ?")
            params.append(self._history_bound(from_raw, end=False))
        if to_raw:
            clauses.append("h.completed_at <= ?")
            params.append(self._history_bound(to_raw, end=True))
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.database.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT
                    h.*,
                    (SELECT COUNT(*) FROM purchase_history_items i WHERE i.purchase_history_id = h.id) AS item_count,
                    (
                        SELECT COUNT(*) FROM purchase_history_items i
                        WHERE i.purchase_history_id = h.id AND i.status = 'purchased'
                    ) AS purchased_count,
                    (
                        SELECT COUNT(*) FROM purchase_history_items i
                        WHERE i.purchase_history_id = h.id AND i.actual_unit_price IS NOT NULL
                    ) AS priced_item_count,
                    (
                        SELECT COUNT(*) FROM purchase_history_items i
                        WHERE i.purchase_history_id = h.id AND i.actual_unit_price IS NULL
                    ) AS unpriced_item_count
                FROM purchase_history h
                {where}
                ORDER BY h.completed_at DESC, h.id DESC
                """,
                params,
            ).fetchall()
        return [self._serialize_history_summary(row) for row in rows]

    def get_history(self, history_id: int) -> dict[str, Any]:
        with self.database.connect() as connection:
            return self._history_detail(connection, history_id)

    def reuse_history(self, history_id: int) -> dict[str, Any]:
        with self.database.connect() as connection:
            history = self._history_detail(connection, history_id)
            now = utc_now()
            cursor = connection.execute(
                """
                INSERT INTO shopping_lists (
                    name, store_name, budget, notes, status, commerce_type_id, store_id, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, 'active', ?, ?, ?, ?)
                """,
                (
                    history["name"],
                    "",
                    0,
                    history.get("notes") or "",
                    history.get("commerce_type_id"),
                    history.get("store_id"),
                    now,
                    now,
                ),
            )
            list_id = int(cursor.lastrowid)
            for position, item in enumerate(history["items"], start=1):
                product_id = self._resolve_product_for_reuse(connection, item)
                payload = self._coerce_item(
                    {
                        "name": item["product_name"],
                        "quantity": item["quantity"],
                        "unit": item["unit"],
                        "category": item["category"] or "Vários",
                        "aisle": item["aisle"] or "Geral",
                        "estimated_price": item["estimated_price"] or 0,
                        "note": item.get("note") or "",
                    }
                )
                self._insert_item(connection, list_id, payload, position, product_id, increment_usage=True)
        return self.get_list(list_id)

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
            self._apply_list_learning(connection, product_id, list_id)
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
        if "actual_unit_price" in payload:
            actual_unit_price = optional_money(payload.get("actual_unit_price"))
        else:
            actual_unit_price = optional_money(current.get("actual_unit_price"))
        now = utc_now()
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE shopping_items
                SET name = ?, quantity = ?, unit = ?, category = ?, aisle = ?, estimated_price = ?,
                    priority = ?, note = ?, status = ?, actual_unit_price = ?, updated_at = ?
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
                    actual_unit_price,
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

    def _sync_product_stores(self, connection, product_id: int, payload: dict[str, Any], replace: bool) -> None:
        if "store_ids" not in payload:
            return
        raw_ids = payload.get("store_ids") or []
        store_ids: list[int] = []
        for value in raw_ids:
            try:
                store_ids.append(int(value))
            except (TypeError, ValueError):
                continue
        store_ids = list(dict.fromkeys(store_ids))
        if replace:
            connection.execute("DELETE FROM product_stores WHERE product_id = ?", (product_id,))
        for store_id in store_ids:
            exists = connection.execute("SELECT id FROM stores WHERE id = ?", (store_id,)).fetchone()
            if exists is None:
                continue
            connection.execute(
                """
                INSERT OR IGNORE INTO product_stores (product_id, store_id, priority)
                VALUES (?, ?, 0)
                """,
                (product_id, store_id),
            )

    def _optional_id(self, value: Any) -> int | None:
        if value in (None, "", 0, "0"):
            return None
        return int(value)

    def _normalize_list_context(
        self, payload: dict[str, Any], current: dict[str, Any] | None = None
    ) -> tuple[int | None, int | None]:
        current = current or {}
        store_id = (
            self._optional_id(payload.get("store_id"))
            if "store_id" in payload
            else self._optional_id(current.get("store_id"))
        )
        type_id = (
            self._optional_id(payload.get("commerce_type_id"))
            if "commerce_type_id" in payload
            else self._optional_id(current.get("commerce_type_id"))
        )
        if store_id is not None:
            store = self.get_store(store_id)
            if not store["is_active"]:
                raise ValueError("A loja está desactivada")
            if "commerce_type_id" in payload:
                requested = self._optional_id(payload.get("commerce_type_id"))
                if requested is not None and requested != store["commerce_type_id"]:
                    raise ValueError("A loja não pertence a esse tipo de comércio")
            type_id = store["commerce_type_id"]
            commerce_type = self.get_commerce_type(type_id)
            if not commerce_type["is_active"]:
                raise ValueError("O tipo de comércio está desactivado")
        elif type_id is not None:
            commerce_type = self.get_commerce_type(type_id)
            if not commerce_type["is_active"]:
                raise ValueError("O tipo de comércio está desactivado")
        return type_id, store_id

    def _apply_list_learning(self, connection, product_id: int, list_id: int) -> None:
        row = connection.execute(
            "SELECT commerce_type_id, store_id FROM shopping_lists WHERE id = ?",
            (list_id,),
        ).fetchone()
        if row is None:
            return
        type_id = row["commerce_type_id"]
        store_id = row["store_id"]
        if not type_id and not store_id:
            return
        if type_id:
            connection.execute(
                """
                INSERT OR IGNORE INTO product_commerce_types (product_id, commerce_type_id, priority)
                VALUES (?, ?, 0)
                """,
                (product_id, type_id),
            )
        if store_id:
            connection.execute(
                """
                INSERT OR IGNORE INTO product_stores (product_id, store_id, priority)
                VALUES (?, ?, 0)
                """,
                (product_id, store_id),
            )

    def _attach_item_context_flags(
        self, connection, items: list[dict[str, Any]], listed: dict[str, Any]
    ) -> None:
        type_id = listed.get("commerce_type_id")
        store_id = listed.get("store_id")
        product_ids = [item["product_id"] for item in items if item.get("product_id")]
        products = attach_product_contexts(connection, [{"id": product_id} for product_id in product_ids])
        by_id = {product["id"]: product for product in products}
        for item in items:
            product = by_id.get(item.get("product_id")) or {}
            type_ids = product.get("commerce_type_ids") or []
            store_ids = product.get("store_ids") or []
            if not type_id and not store_id:
                item["in_context"] = True
            elif store_id:
                item["in_context"] = store_id in store_ids or type_id in type_ids
            else:
                item["in_context"] = type_id in type_ids

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

    def _list_row(self, connection, list_id: int):
        row = connection.execute(
            """
            SELECT
                l.*,
                c.name AS commerce_type_name,
                s.name AS location_store_name
            FROM shopping_lists l
            LEFT JOIN commerce_types c ON c.id = l.commerce_type_id
            LEFT JOIN stores s ON s.id = l.store_id
            WHERE l.id = ?
            """,
            (list_id,),
        ).fetchone()
        if row is None:
            raise KeyError("List not found")
        return row

    def _history_item_snapshot(self, connection, item, position: int, now: str) -> dict[str, Any]:
        product_id = item["product_id"]
        subcategory = ""
        if product_id:
            product = connection.execute(
                "SELECT subcategory FROM products WHERE id = ?",
                (product_id,),
            ).fetchone()
            if product is not None:
                subcategory = product["subcategory"] or ""
        actual_unit_price = optional_money(item["actual_unit_price"] if "actual_unit_price" in item.keys() else None)
        quantity = float(item["quantity"] or 0)
        actual_line_total = round(quantity * actual_unit_price, 2) if actual_unit_price is not None else None
        return {
            "product_id": product_id,
            "product_name": item["name"],
            "category": item["category"] or "",
            "subcategory": subcategory,
            "quantity": quantity,
            "unit": item["unit"] or "un",
            "estimated_price": float(item["estimated_price"] or 0),
            "actual_unit_price": actual_unit_price,
            "actual_line_total": actual_line_total,
            "status": item["status"] or "pending",
            "aisle": item["aisle"] or "",
            "note": item["note"] or "",
            "position": position,
            "created_at": now,
        }

    def _complete_payload(self, connection, history_id: int) -> dict[str, Any]:
        detail = self._history_detail(connection, history_id)
        return {
            "history_id": detail["id"],
            "completed_at": detail["completed_at"],
            "item_count": detail["item_count"],
            "purchased_count": detail["purchased_count"],
            "actual_total": detail["actual_total"],
            "priced_item_count": detail["priced_item_count"],
            "unpriced_item_count": detail["unpriced_item_count"],
            "estimated_total": detail["estimated_total"],
            "source_list_id": detail["source_list_id"],
        }

    def _history_detail(self, connection, history_id: int) -> dict[str, Any]:
        row = connection.execute(
            "SELECT * FROM purchase_history WHERE id = ?",
            (history_id,),
        ).fetchone()
        if row is None:
            raise KeyError("History not found")
        items = connection.execute(
            """
            SELECT *
            FROM purchase_history_items
            WHERE purchase_history_id = ?
            ORDER BY position ASC, id ASC
            """,
            (history_id,),
        ).fetchall()
        serialized = [self._serialize_history_item(item) for item in items]
        purchased = sum(1 for item in serialized if item["status"] == "purchased")
        priced = sum(1 for item in serialized if item["actual_unit_price"] is not None)
        return {
            "id": row["id"],
            "source_list_id": row["source_list_id"],
            "name": row["name"],
            "completed_at": row["completed_at"],
            "commerce_type_id": row["commerce_type_id"],
            "store_id": row["store_id"],
            "commerce_type_name": row["commerce_type_name"] or "",
            "store_name": row["store_name"] or "",
            "estimated_total": round(row["estimated_total"] or 0, 2),
            "actual_total": None if row["actual_total"] is None else round(row["actual_total"], 2),
            "notes": row["notes"] or "",
            "created_at": row["created_at"],
            "item_count": len(serialized),
            "purchased_count": purchased,
            "priced_item_count": priced,
            "unpriced_item_count": len(serialized) - priced,
            "items": serialized,
        }

    def _serialize_history_summary(self, row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "name": row["name"],
            "completed_at": row["completed_at"],
            "store_name": row["store_name"] or "",
            "commerce_type_name": row["commerce_type_name"] or "",
            "commerce_type_id": row["commerce_type_id"],
            "store_id": row["store_id"],
            "item_count": int(row["item_count"] or 0),
            "purchased_count": int(row["purchased_count"] or 0),
            "estimated_total": round(row["estimated_total"] or 0, 2),
            "actual_total": None if row["actual_total"] is None else round(row["actual_total"], 2),
            "priced_item_count": int(row["priced_item_count"] or 0) if "priced_item_count" in row.keys() else 0,
            "unpriced_item_count": int(row["unpriced_item_count"] or 0) if "unpriced_item_count" in row.keys() else 0,
        }

    def _serialize_history_item(self, row) -> dict[str, Any]:
        actual_unit_price = optional_money(row["actual_unit_price"])
        quantity = float(row["quantity"] or 0)
        stored_total = row["actual_line_total"]
        if actual_unit_price is None:
            actual_line_total = None
        elif stored_total is not None:
            actual_line_total = round(float(stored_total), 2)
        else:
            actual_line_total = round(quantity * actual_unit_price, 2)
        return {
            "id": row["id"],
            "purchase_history_id": row["purchase_history_id"],
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "category": row["category"] or "",
            "subcategory": row["subcategory"] or "",
            "quantity": quantity,
            "unit": row["unit"] or "un",
            "estimated_price": float(row["estimated_price"] or 0),
            "actual_unit_price": actual_unit_price,
            "actual_line_total": actual_line_total,
            "status": row["status"],
            "aisle": row["aisle"] or "",
            "note": row["note"] or "",
            "position": row["position"],
        }

    def _history_bound(self, value: str, *, end: bool) -> str:
        if "T" in value or " " in value:
            return value
        return f"{value}T23:59:59.999999+00:00" if end else f"{value}T00:00:00+00:00"

    def _resolve_product_for_reuse(self, connection, item: dict[str, Any]) -> int:
        product_id = item.get("product_id")
        if product_id:
            row = connection.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if row is not None:
                if not row["is_active"]:
                    connection.execute(
                        "UPDATE products SET is_active = 1, updated_at = ? WHERE id = ?",
                        (utc_now(), product_id),
                    )
                return int(row["id"])
        found = self._find_product_row(connection, item.get("product_name") or "")
        if found is not None:
            if not found["is_active"]:
                connection.execute(
                    "UPDATE products SET is_active = 1, updated_at = ? WHERE id = ?",
                    (utc_now(), int(found["id"])),
                )
            return int(found["id"])
        payload = ProductPayload(
            name=normalize_name(item.get("product_name") or "") or "Novo produto",
            category=canonicalize_category(item.get("category") or "Vários"),
            subcategory=(item.get("subcategory") or "").strip(),
            default_unit=normalize_text(item.get("unit") or "", "un"),
            default_quantity=float(item.get("quantity") or 1),
            default_estimated_price=float(item.get("estimated_price") or 0),
        )
        return self._insert_product(connection, payload)

    def _attach_product_insights(self, connection, products: list[dict[str, Any]]) -> None:
        if not products or not _table_exists(connection, "purchase_history_items"):
            for product in products:
                product.setdefault("last_purchased_at", None)
                product.setdefault("last_actual_price", None)
                product.setdefault("purchase_count", 0)
            return
        ids = [int(product["id"]) for product in products]
        placeholders = ",".join("?" * len(ids))
        stats = connection.execute(
            f"""
            SELECT
                i.product_id,
                MAX(CASE WHEN i.status = 'purchased' THEN h.completed_at END) AS last_purchased_at,
                SUM(CASE WHEN i.status = 'purchased' THEN 1 ELSE 0 END) AS purchase_count
            FROM purchase_history_items i
            JOIN purchase_history h ON h.id = i.purchase_history_id
            WHERE i.product_id IN ({placeholders})
            GROUP BY i.product_id
            """,
            ids,
        ).fetchall()
        stats_by_id = {int(row["product_id"]): row for row in stats if row["product_id"] is not None}
        prices = connection.execute(
            f"""
            SELECT i.product_id, i.actual_unit_price
            FROM purchase_history_items i
            JOIN purchase_history h ON h.id = i.purchase_history_id
            WHERE i.product_id IN ({placeholders}) AND i.actual_unit_price IS NOT NULL
            ORDER BY h.completed_at DESC, i.id DESC
            """,
            ids,
        ).fetchall()
        last_price: dict[int, float] = {}
        for row in prices:
            product_id = int(row["product_id"])
            if product_id not in last_price:
                last_price[product_id] = round(float(row["actual_unit_price"]), 2)
        for product in products:
            product_id = int(product["id"])
            row = stats_by_id.get(product_id)
            product["last_purchased_at"] = row["last_purchased_at"] if row else None
            product["purchase_count"] = int(row["purchase_count"] or 0) if row else 0
            product["last_actual_price"] = last_price.get(product_id)

    def _serialize_list(self, row) -> dict[str, Any]:
        keys = row.keys()
        commerce_type_id = row["commerce_type_id"] if "commerce_type_id" in keys else None
        store_id = row["store_id"] if "store_id" in keys else None
        commerce_type_name = row["commerce_type_name"] if "commerce_type_name" in keys else None
        location_store_name = row["location_store_name"] if "location_store_name" in keys else None
        history_id = row["history_id"] if "history_id" in keys else None
        if location_store_name and commerce_type_name:
            location_label = f"{location_store_name} · {commerce_type_name}"
        elif location_store_name:
            location_label = location_store_name
        elif commerce_type_name:
            location_label = commerce_type_name
        else:
            location_label = "Todos os locais"
        return {
            "id": row["id"],
            "name": row["name"],
            "store_name": row["store_name"],
            "budget": row["budget"],
            "notes": row["notes"],
            "status": row["status"],
            "commerce_type_id": commerce_type_id,
            "store_id": store_id,
            "commerce_type_name": commerce_type_name,
            "location_store_name": location_store_name,
            "location_label": location_label,
            "location_short": location_store_name or commerce_type_name or "Todos",
            "history_id": history_id,
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
        actual = optional_money(data.get("actual_unit_price"))
        data["actual_unit_price"] = actual
        data["actual_line_total"] = round(data["quantity"] * actual, 2) if actual is not None else None
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
        priced = [item for item in items if item.get("actual_unit_price") is not None]
        actual_total = round(sum(item["actual_line_total"] or 0 for item in priced), 2) if priced else None
        return {
            "estimated_total": total,
            "actual_total": actual_total,
            "priced_item_count": len(priced),
            "unpriced_item_count": len(items) - len(priced),
            "budget_remaining": round(budget - total, 2),
            "purchased_count": purchased,
            "in_cart_count": in_cart,
            "pending_count": pending,
            "aisles": sorted({item["aisle"] for item in items}),
            "completion_rate": round((purchased / len(items)) * 100, 1) if items else 0,
        }
