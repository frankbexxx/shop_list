import sqlite3
from kivy.event import EventDispatcher
from db_config import DatabaseConfig

class DatabaseManager(EventDispatcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = DatabaseConfig()
        self.connection = None
        self._initialize_database()
        
    def _initialize_database(self):
        self.connection = sqlite3.connect(self.config.config['database'])
        self._create_tables()
        
    def _create_tables(self):
        cursor = self.connection.cursor()
        for table_name, table_info in self.config.config['tables'].items():
            columns = ', '.join([f"{col[0]} {col[1]}" for col in table_info['columns']])
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            cursor.execute(query)
        self.connection.commit()
        
    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.connection.commit()
        return cursor
