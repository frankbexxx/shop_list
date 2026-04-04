from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "web"
DEFAULT_DB_PATH = DATA_DIR / "shopping_list.sqlite3"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
