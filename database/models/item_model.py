from base_model import BaseModel
from kivy.properties import (
    StringProperty, 
    NumericProperty, 
    BooleanProperty
)

class ItemModel(BaseModel):
    name = StringProperty('')
    quantity = NumericProperty(1)
    price = NumericProperty(0)
    category_id = StringProperty('')
    is_checked = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_item()
        
    def _setup_item(self):
        self.bind(
            quantity=self._update_total,
            price=self._update_total
        )
