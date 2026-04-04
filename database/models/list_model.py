from base_model import BaseModel
from kivy.properties import StringProperty, ListProperty, NumericProperty

class ListModel(BaseModel):
    name = StringProperty('')
    description = StringProperty('')
    items = ListProperty([])
    total = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_list()
        
    def _setup_list(self):
        self.bind(
            items=self._calculate_total
        )
