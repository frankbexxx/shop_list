import sqlite3
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

class SQLiteManager(EventDispatcher):
    connection = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_database()
        
    def _setup_database(self):
        self.database_path = 'shopping_list.db'
        self.connection = sqlite3.connect(self.database_path)
        self.cursor = self.connection.cursor()
