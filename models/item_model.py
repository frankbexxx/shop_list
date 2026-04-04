from base_model import BaseModel
from kivy.properties import (
    StringProperty, 
    NumericProperty, 
    BooleanProperty,
    DictProperty
)

class ItemModel(BaseModel):
    name = StringProperty('')
    category_id = StringProperty('')
    price = NumericProperty(0)
    quantity = NumericProperty(1)
    is_checked = BooleanProperty(False)
    details = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_item()
        
    def _setup_item(self):
        self.details = {
            'unit': 'piece',
            'brand': '',
            'notes': '',
            'priority': 'normal'
        }
        
    def calculate_total(self):
        return self.price * self.quantity
        
    def toggle_check(self):
        self.is_checked = not self.is_checked
