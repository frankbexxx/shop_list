from base_model import BaseModel
from kivy.properties import (
    StringProperty, 
    ListProperty, 
    DictProperty,
    ColorProperty
)

class CategoryModel(BaseModel):
    name = StringProperty('')
    icon = StringProperty('default')
    color = ColorProperty([1, 1, 1, 1])
    items = ListProperty([])
    attributes = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_category()
        
    def _setup_category(self):
        self.attributes = {
            'display_order': 0,
            'is_custom': True,
            'parent_id': None,
            'subcategories': []
        }
        
    def add_item(self, item_id):
        if item_id not in self.items:
            self.items.append(item_id)
            
    def remove_item(self, item_id):
        if item_id in self.items:
            self.items.remove(item_id)
