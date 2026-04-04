from base_model import BaseModel
from kivy.properties import StringProperty, ListProperty

class CategoryModel(BaseModel):
    name = StringProperty('')
    icon = StringProperty('')
    color = StringProperty('#2196F3')
    items = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_category()
        
    def _setup_category(self):
        self.bind(
            items=self._update_items_count
        )
