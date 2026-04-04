import unittest
from database.models.base_model import BaseModel
from database.models.list_model import ListModel
from database.models.item_model import ItemModel

class TestModels(unittest.TestCase):
    def setUp(self):
        self.list_model = ListModel()
        self.item_model = ItemModel()
        
    def test_base_model_initialization(self):
        model = BaseModel()
        self.assertIsNotNone(model.id)
        self.assertIsNotNone(model.created_at)
