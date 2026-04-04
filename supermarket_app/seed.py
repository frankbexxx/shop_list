from pathlib import Path
import json


DEFAULT_CATEGORIES = [
    {"name": "Fresh Produce", "aisle": "Produce", "color": "#4d7c0f"},
    {"name": "Bakery", "aisle": "Bakery", "color": "#b45309"},
    {"name": "Dairy & Eggs", "aisle": "Dairy", "color": "#0369a1"},
    {"name": "Meat & Fish", "aisle": "Butcher", "color": "#b91c1c"},
    {"name": "Frozen", "aisle": "Frozen", "color": "#0f766e"},
    {"name": "Pantry", "aisle": "Pantry", "color": "#7c3aed"},
    {"name": "Household", "aisle": "Household", "color": "#475569"},
]

DEFAULT_TEMPLATES = [
    {"name": "Milk", "category": "Dairy & Eggs", "aisle": "Dairy", "unit": "L", "quantity": 1},
    {"name": "Eggs", "category": "Dairy & Eggs", "aisle": "Dairy", "unit": "box", "quantity": 1},
    {"name": "Bread", "category": "Bakery", "aisle": "Bakery", "unit": "unit", "quantity": 1},
    {"name": "Bananas", "category": "Fresh Produce", "aisle": "Produce", "unit": "kg", "quantity": 1},
    {"name": "Pasta", "category": "Pantry", "aisle": "Pantry", "unit": "pack", "quantity": 1},
]


def _load_json(path: Path, root_key: str) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get(root_key, [])


def load_seed_data(base_dir: Path) -> tuple[list[dict], list[dict]]:
    categories_path = base_dir / "assets" / "data" / "categories.json"
    items_path = base_dir / "assets" / "data" / "default_items.json"

    categories = DEFAULT_CATEGORIES.copy()
    for item in _load_json(categories_path, "categories"):
        categories.append(
            {
                "name": item.get("name", "Other"),
                "aisle": item.get("name", "General"),
                "color": item.get("color", "#64748b"),
            }
        )

    templates = DEFAULT_TEMPLATES.copy()
    for item in _load_json(items_path, "items"):
        templates.append(
            {
                "name": item.get("name", "Unnamed"),
                "category": "Groceries",
                "aisle": "General",
                "unit": item.get("unit", "unit"),
                "quantity": item.get("default_quantity", 1),
            }
        )

    return categories, templates
