import unicodedata
from typing import Any


COMMERCE_TYPE_SEED = [
    {"name": "Supermercado", "slug": "supermercado", "description": "Hipermercados e supermercados", "icon": "cart", "position": 1},
    {"name": "Mercearia", "slug": "mercearia", "description": "Mini-mercados e mercearias", "icon": "bag", "position": 2},
    {"name": "Bricolage", "slug": "bricolage", "description": "Ferragens e bricolage", "icon": "tool", "position": 3},
    {"name": "Tecnologia", "slug": "tecnologia", "description": "Electrónica e informática", "icon": "device", "position": 4},
    {"name": "Farmácia", "slug": "farmacia", "description": "Farmácia e parafarmácia", "icon": "cross", "position": 5},
    {"name": "Papelaria", "slug": "papelaria", "description": "Papelaria e escritório", "icon": "paper", "position": 6},
    {"name": "Casa", "slug": "casa", "description": "Casa e decoração", "icon": "home", "position": 7},
    {"name": "Outros", "slug": "outros", "description": "Outros contextos de compra", "icon": "more", "position": 8},
]

STORE_SEED = [
    ("Continente", "supermercado"),
    ("Auchan", "supermercado"),
    ("Pingo Doce", "supermercado"),
    ("Lidl", "supermercado"),
    ("Aldi", "supermercado"),
    ("Intermarché", "supermercado"),
    ("Leroy Merlin", "bricolage"),
    ("Bricomarché", "bricolage"),
    ("MaxMat", "bricolage"),
    ("Worten", "tecnologia"),
    ("Rádio Popular", "tecnologia"),
    ("Fnac", "tecnologia"),
    ("Staples", "papelaria"),
    ("Wells", "farmacia"),
]

# Extra contexts beyond the default Supermercado. Conservative substrings only.
EXTRA_TYPE_KEYWORDS = [
    (("pilha",), ("bricolage", "tecnologia")),
    (("lampad", "lâmpad"), ("bricolage", "casa")),
    (("caderno", "caneta", "lápis", "lapis", "marcador"), ("papelaria",)),
]


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    slug = []
    previous_dash = False
    for char in ascii_text.lower():
        if char.isalnum():
            slug.append(char)
            previous_dash = False
        elif not previous_dash:
            slug.append("-")
            previous_dash = True
    return "".join(slug).strip("-") or "local"


def extra_type_slugs_for_name(name: str) -> list[str]:
    lowered = (name or "").casefold()
    slugs: list[str] = []
    for needles, extras in EXTRA_TYPE_KEYWORDS:
        if any(needle in lowered for needle in needles):
            slugs.extend(extras)
    return list(dict.fromkeys(slugs))


def seed_locations(connection, now: str) -> None:
    for item in COMMERCE_TYPE_SEED:
        connection.execute(
            """
            INSERT OR IGNORE INTO commerce_types
                (name, slug, description, icon, position, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (item["name"], item["slug"], item["description"], item["icon"], item["position"], now, now),
        )

    types = {
        row["slug"]: row["id"]
        for row in connection.execute("SELECT id, slug FROM commerce_types").fetchall()
    }
    for name, type_slug in STORE_SEED:
        type_id = types.get(type_slug)
        if type_id is None:
            continue
        connection.execute(
            """
            INSERT OR IGNORE INTO stores
                (name, commerce_type_id, slug, notes, is_active, created_at, updated_at)
            VALUES (?, ?, ?, '', 1, ?, ?)
            """,
            (name, type_id, slugify(name), now, now),
        )


def migrate_product_contexts(connection) -> None:
    existing_links = connection.execute(
        "SELECT COUNT(*) AS total FROM product_commerce_types"
    ).fetchone()["total"]
    if existing_links:
        return
    types = {
        row["slug"]: row["id"]
        for row in connection.execute("SELECT id, slug FROM commerce_types").fetchall()
    }
    supermarket_id = types.get("supermercado")
    if supermarket_id is None:
        return
    products = connection.execute("SELECT id, name FROM products").fetchall()
    for product in products:
        connection.execute(
            """
            INSERT OR IGNORE INTO product_commerce_types (product_id, commerce_type_id, priority)
            VALUES (?, ?, 0)
            """,
            (product["id"], supermarket_id),
        )
        for slug in extra_type_slugs_for_name(product["name"]):
            type_id = types.get(slug)
            if type_id is None:
                continue
            connection.execute(
                """
                INSERT OR IGNORE INTO product_commerce_types (product_id, commerce_type_id, priority)
                VALUES (?, ?, 0)
                """,
                (product["id"], type_id),
            )


def attach_product_contexts(connection, products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not products:
        return products
    ids = [product["id"] for product in products]
    placeholders = ",".join("?" * len(ids))
    type_rows = connection.execute(
        f"""
        SELECT product_id, commerce_type_id
        FROM product_commerce_types
        WHERE product_id IN ({placeholders})
        ORDER BY commerce_type_id
        """,
        ids,
    ).fetchall()
    store_rows = connection.execute(
        f"""
        SELECT product_id, store_id
        FROM product_stores
        WHERE product_id IN ({placeholders})
        ORDER BY store_id
        """,
        ids,
    ).fetchall()
    types_map: dict[int, list[int]] = {product_id: [] for product_id in ids}
    stores_map: dict[int, list[int]] = {product_id: [] for product_id in ids}
    for row in type_rows:
        types_map[row["product_id"]].append(row["commerce_type_id"])
    for row in store_rows:
        stores_map[row["product_id"]].append(row["store_id"])
    for product in products:
        product["commerce_type_ids"] = types_map.get(product["id"], [])
        product["store_ids"] = stores_map.get(product["id"], [])
    return products
