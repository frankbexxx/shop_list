import unittest
from database.managers.sqlite_manager import SQLiteManager
from database.managers.query_builder import QueryBuilder

class TestManagers(unittest.TestCase):
    def setUp(self):
        self.db_manager = SQLiteManager()
        self.query_builder = QueryBuilder()
        
    def test_database_connection(self):
        self.assertIsNotNone(self.db_manager.connection)
        self.assertTrue(self.db_manager.connection.total_changes >= 0)
