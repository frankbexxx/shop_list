from kivy.event import EventDispatcher
from kivy.properties import ListProperty

class MigrationManager(EventDispatcher):
    migrations = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_migrations()
        
    def _setup_migrations(self):
        self.migrations = [
            self._create_users_table,
            self._create_lists_table,
            self._create_items_table,
            self._create_categories_table
        ]
