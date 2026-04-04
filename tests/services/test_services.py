import unittest
from database.services.crud_service import CRUDService
from database.services.validation_service import ValidationService

class TestServices(unittest.TestCase):
    def setUp(self):
        self.crud_service = CRUDService()
        self.validation_service = ValidationService()
        
    def test_crud_operations(self):
        test_data = {'name': 'Test List', 'items': []}
        created = self.crud_service.operations['create'](test_data)
        self.assertIsNotNone(created.id)
