import sqlite3
from contextlib import contextmanager
from pathlib import Path


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS shopping_lists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    store_name TEXT NOT NULL DEFAULT '',
                    budget REAL NOT NULL DEFAULT 0,
                    notes TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'active',
                    commerce_type_id INTEGER,
                    store_id INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS shopping_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    list_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    quantity REAL NOT NULL DEFAULT 1,
                    unit TEXT NOT NULL DEFAULT 'unit',
                    category TEXT NOT NULL DEFAULT 'Pantry',
                    aisle TEXT NOT NULL DEFAULT 'General',
                    estimated_price REAL NOT NULL DEFAULT 0,
                    priority INTEGER NOT NULL DEFAULT 2,
                    note TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'pending',
                    position INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (list_id) REFERENCES shopping_lists(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS item_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    aisle TEXT NOT NULL,
                    unit TEXT NOT NULL DEFAULT 'unit',
                    default_quantity REAL NOT NULL DEFAULT 1,
                    times_used INTEGER NOT NULL DEFAULT 0,
                    last_used_at TEXT
                );

                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'Vários',
                    subcategory TEXT NOT NULL DEFAULT '',
                    default_unit TEXT NOT NULL DEFAULT 'un',
                    default_quantity REAL NOT NULL DEFAULT 1,
                    default_estimated_price REAL NOT NULL DEFAULT 0,
                    default_priority INTEGER NOT NULL DEFAULT 2,
                    notes TEXT NOT NULL DEFAULT '',
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_used_at TEXT,
                    times_used INTEGER NOT NULL DEFAULT 0
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_products_name_nocase
                    ON products(name COLLATE NOCASE);

                CREATE TABLE IF NOT EXISTS commerce_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    slug TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL DEFAULT '',
                    icon TEXT NOT NULL DEFAULT '',
                    position INTEGER NOT NULL DEFAULT 0,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS stores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    commerce_type_id INTEGER NOT NULL,
                    slug TEXT NOT NULL UNIQUE,
                    notes TEXT NOT NULL DEFAULT '',
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (commerce_type_id) REFERENCES commerce_types(id)
                );

                CREATE TABLE IF NOT EXISTS product_commerce_types (
                    product_id INTEGER NOT NULL,
                    commerce_type_id INTEGER NOT NULL,
                    priority INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (product_id, commerce_type_id),
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    FOREIGN KEY (commerce_type_id) REFERENCES commerce_types(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS product_stores (
                    product_id INTEGER NOT NULL,
                    store_id INTEGER NOT NULL,
                    priority INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (product_id, store_id),
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS purchase_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_list_id INTEGER UNIQUE,
                    name TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    commerce_type_id INTEGER,
                    store_id INTEGER,
                    commerce_type_name TEXT NOT NULL DEFAULT '',
                    store_name TEXT NOT NULL DEFAULT '',
                    estimated_total REAL NOT NULL DEFAULT 0,
                    actual_total REAL,
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (source_list_id) REFERENCES shopping_lists(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS purchase_history_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    purchase_history_id INTEGER NOT NULL,
                    product_id INTEGER,
                    product_name TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT '',
                    subcategory TEXT NOT NULL DEFAULT '',
                    quantity REAL NOT NULL DEFAULT 1,
                    unit TEXT NOT NULL DEFAULT 'un',
                    estimated_price REAL NOT NULL DEFAULT 0,
                    actual_unit_price REAL,
                    actual_line_total REAL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    aisle TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    position INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (purchase_history_id) REFERENCES purchase_history(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_purchase_history_completed
                    ON purchase_history(completed_at DESC);

                CREATE INDEX IF NOT EXISTS idx_purchase_history_items_product
                    ON purchase_history_items(product_id);

                CREATE INDEX IF NOT EXISTS idx_purchase_history_items_history
                    ON purchase_history_items(purchase_history_id);
                """
            )
            self._ensure_column(connection, "shopping_items", "product_id", "INTEGER")
            self._ensure_column(connection, "shopping_lists", "commerce_type_id", "INTEGER")
            self._ensure_column(connection, "shopping_lists", "store_id", "INTEGER")
            self._ensure_column(connection, "shopping_items", "actual_unit_price", "REAL")

    def _ensure_column(self, connection, table: str, column: str, definition: str) -> None:
        rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
        if any(row["name"] == column for row in rows):
            return
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
