from kivy.properties import DictProperty
from kivy.event import EventDispatcher

class DatabaseConfig(EventDispatcher):
    config = DictProperty({
        'database': 'shopping_list.db',
        'version': '1.0',
        'tables': {
            'users': {
                'columns': [
                    ('id', 'TEXT PRIMARY KEY'),
                    ('username', 'TEXT NOT NULL'),
                    ('email', 'TEXT UNIQUE'),
                    ('preferences', 'TEXT'),
                    ('created_at', 'TEXT'),
                    ('updated_at', 'TEXT')
                ]
            },
            'lists': {
                'columns': [
                    ('id', 'TEXT PRIMARY KEY'),
                    ('name', 'TEXT NOT NULL'),
                    ('owner_id', 'TEXT'),
                    ('items', 'TEXT'),
                    ('created_at', 'TEXT'),
                    ('updated_at', 'TEXT')
                ]
            }
        }
    })
