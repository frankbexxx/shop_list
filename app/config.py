from pathlib import Path

# Application Settings
APP_NAME = "Shopping List"
APP_VERSION = "1.0.0"
DEBUG = True

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# UI Settings
WINDOW_CONFIG = {
    'minimum_width': 300,
    'minimum_height': 500,
    'default_width': 400,
    'default_height': 600,
    'resizable': True
}

# Theme Colors
COLORS = {
    'primary': '#2196F3',
    'secondary': '#FF9800',
    'success': '#4CAF50',
    'warning': '#FFC107',
    'error': '#F44336',
    'background': '#FFFFFF',
    'text': '#000000'
}

# Database Settings
DB_CONFIG = {
    'type': 'sqlite',
    'name': 'shopping_list.db',
    'path': DATA_DIR
}

# Platform specific settings
PLATFORM_SETTINGS = {
    'android': {
        'font_size': 18,
        'touch_target': 48
    },
    'desktop': {
        'font_size': 14,
        'touch_target': 32
    }
}
