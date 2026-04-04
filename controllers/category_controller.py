from base_controller import BaseController
from kivy.properties import ListProperty, DictProperty

class CategoryController(BaseController):
    categories = ListProperty([])
    category_hierarchy = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_category_controller()
        
    def _setup_category_controller(self):
        self.category_actions = {
            'create_category': self.create_category,
            'update_category': self.update_category,
            'delete_category': self.delete_category,
            'assign_items': self.assign_items,
            'reorder_categories': self.reorder_categories
        }
        
    def create_category(self, category_data):
        if self.validate_category_data(category_data):
            new_category = self._create_category_object(category_data)
            self.categories.append(new_category)
            return new_category
        return None
