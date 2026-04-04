from kivy.event import EventDispatcher
from kivy.properties import DictProperty

class DatabaseQueries(EventDispatcher):
    queries = DictProperty({
        'users': {
            'create': """
                INSERT INTO users (id, username, email, preferences, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            'get': "SELECT * FROM users WHERE id = ?",
            'update': """
                UPDATE users 
                SET username = ?, email = ?, preferences = ?, updated_at = ?
                WHERE id = ?
            """,
            'delete': "DELETE FROM users WHERE id = ?"
        },
        'lists': {
            'create': """
                INSERT INTO lists (id, name, owner_id, items, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            'get': "SELECT * FROM lists WHERE id = ?",
            'update': """
                UPDATE lists 
                SET name = ?, items = ?, updated_at = ?
                WHERE id = ?
            """,
            'delete': "DELETE FROM lists WHERE id = ?"
        }
    })
