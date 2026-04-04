from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .database import Database


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_text(value: str, fallback: str) -> str:
    cleaned = (value or "").strip()
    return cleaned or fallback


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
    category: str = "Pantry"
    aisle: str = "General"
    estimated_price: float = 0
    priority: int = 2
    note: str = ""


class ShoppingService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def bootstrap(self, categories: list[dict], templates: list[dict]) -> None:
        self.database.initialize()
        with self.database.connect() as connection:
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

            for template in templates:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO item_templates (name, category, aisle, unit, default_quantity)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        template["name"],
                        template["category"],
                        template["aisle"],
                        template["unit"],
                        template["quantity"],
                    ),
                )

            active_list_id = self._get_default_list_id(connection)
            item_total = connection.execute(
                "SELECT COUNT(*) AS total FROM shopping_items WHERE list_id = ?",
                (active_list_id,),
            ).fetchone()["total"]
            if item_total == 0:
                for position, template in enumerate(templates[:5], start=1):
                    self._insert_item(connection, active_list_id, ItemPayload(**template), position)

    def dashboard(self) -> dict[str, Any]:
        lists = self.list_lists()
        return {
            "lists": lists,
            "active_list_id": lists[0]["id"] if lists else None,
            "suggestions": self.suggestions(),
        }

    def list_lists(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    l.*,
                    COUNT(i.id) AS item_count,
                    SUM(CASE WHEN i.status = 'purchased' THEN 1 ELSE 0 END) AS purchased_count,
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
            item_rows = connection.execute(
                """
                SELECT *
                FROM shopping_items
                WHERE list_id = ?
                ORDER BY
                    CASE status WHEN 'pending' THEN 0 WHEN 'in_cart' THEN 1 ELSE 2 END,
                    aisle ASC,
                    priority ASC,
                    position ASC,
                    name COLLATE NOCASE ASC
                """,
                (list_id,),
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
        with self.database.connect() as connection:
            position = connection.execute(
                "SELECT COALESCE(MAX(position), 0) + 1 AS next_position FROM shopping_items WHERE list_id = ?",
                (list_id,),
            ).fetchone()["next_position"]
            item_id = self._insert_item(connection, list_id, self._coerce_item(payload), position)
            connection.execute("UPDATE shopping_lists SET updated_at = ? WHERE id = ?", (utc_now(), list_id))
        return self.get_item(item_id)

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
            if status == "purchased":
                self._register_template_use(connection, data.name, data.category, data.aisle, data.unit, data.quantity)
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
                SELECT *
                FROM item_templates
                ORDER BY times_used DESC, name COLLATE NOCASE ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def _coerce_item(self, payload: dict[str, Any]) -> ItemPayload:
        quantity = float(payload.get("quantity", 1) or 1)
        estimated_price = float(payload.get("estimated_price", 0) or 0)
        priority = int(payload.get("priority", 2) or 2)
        priority = min(max(priority, 1), 3)
        return ItemPayload(
            name=normalize_text(payload.get("name", ""), "New item"),
            quantity=quantity,
            unit=normalize_text(payload.get("unit", ""), "unit"),
            category=normalize_text(payload.get("category", ""), "Pantry"),
            aisle=normalize_text(payload.get("aisle", ""), "General"),
            estimated_price=estimated_price,
            priority=priority,
            note=(payload.get("note") or "").strip(),
        )

    def _get_default_list_id(self, connection) -> int:
        row = connection.execute(
            "SELECT id FROM shopping_lists ORDER BY CASE status WHEN 'active' THEN 0 ELSE 1 END, updated_at DESC LIMIT 1"
        ).fetchone()
        return int(row["id"])

    def _insert_item(self, connection, list_id: int, payload: ItemPayload, position: int) -> int:
        now = utc_now()
        cursor = connection.execute(
            """
            INSERT INTO shopping_items (
                list_id, name, quantity, unit, category, aisle, estimated_price, priority, note,
                status, position, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)
            """,
            (
                list_id,
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
        self._register_template_use(connection, payload.name, payload.category, payload.aisle, payload.unit, payload.quantity)
        return int(cursor.lastrowid)

    def _register_template_use(self, connection, name: str, category: str, aisle: str, unit: str, quantity: float) -> None:
        now = utc_now()
        connection.execute(
            """
            INSERT INTO item_templates (name, category, aisle, unit, default_quantity, times_used, last_used_at)
            VALUES (?, ?, ?, ?, ?, 1, ?)
            ON CONFLICT(name) DO UPDATE SET
                category = excluded.category,
                aisle = excluded.aisle,
                unit = excluded.unit,
                default_quantity = excluded.default_quantity,
                times_used = item_templates.times_used + 1,
                last_used_at = excluded.last_used_at
            """,
            (name, category, aisle, unit, quantity, now),
        )

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
            "item_count": row["item_count"],
            "purchased_count": row["purchased_count"] or 0,
            "estimated_total": round(row["estimated_total"] or 0, 2),
        }

    def _serialize_item(self, row) -> dict[str, Any]:
        data = dict(row)
        data["line_total"] = round(data["quantity"] * data["estimated_price"], 2)
        return data

    def _summarize_items(self, items: list[dict[str, Any]], budget: float) -> dict[str, Any]:
        total = round(sum(item["line_total"] for item in items), 2)
        purchased = sum(1 for item in items if item["status"] == "purchased")
        return {
            "estimated_total": total,
            "budget_remaining": round(budget - total, 2),
            "purchased_count": purchased,
            "pending_count": sum(1 for item in items if item["status"] != "purchased"),
            "aisles": sorted({item["aisle"] for item in items}),
            "completion_rate": round((purchased / len(items)) * 100, 1) if items else 0,
        }
