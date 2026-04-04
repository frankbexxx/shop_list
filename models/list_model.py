from base_model import BaseModel
from kivy.properties import (
    StringProperty, 
    ListProperty, 
    NumericProperty, 
    BooleanProperty
)

class ListModel(BaseModel):
    name = StringProperty('')
    owner_id = StringProperty('')
    items = ListProperty([])
    total = NumericProperty(0)
    is_shared = BooleanProperty(False)
    shared_with = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_list()
        
    def _setup_list(self):
        self.categories = []
        self.tags = []
        self.status = 'active'
        
    def add_item(self, item):
        self.items.append(item)
        self._update_total()
        
    def remove_item(self, item_id):
        self.items = [item for item in self.items if item['id'] != item_id]
        self._update_total()
        
    def _update_total(self):
        self.total = sum(item['price'] * item['quantity'] for item in self.items)
