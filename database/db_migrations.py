from kivy.event import EventDispatcher
from kivy.properties import ListProperty, StringProperty

class DatabaseMigrations(EventDispatcher):
    migrations = ListProperty([])
    current_version = StringProperty('1.0')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_migrations()
        
    def _setup_migrations(self):
        self.migrations = [
            {
                'version': '1.0',
                'up': [
                    """
                    CREATE TABLE IF NOT EXISTS migrations (
                        version TEXT PRIMARY KEY,
                        applied_at TEXT
                    )
                    """
                ],
                'down': [
                    "DROP TABLE IF EXISTS migrations"
                ]
            },
            {
                'version': '1.1',
                'up': [
                    """
                    ALTER TABLE users 
                    ADD COLUMN last_login TEXT
                    """
                ],
                'down': [
                    """
                    ALTER TABLE users 
                    DROP COLUMN last_login
                    """
                ]
            }
        ]
