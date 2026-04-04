from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, ListProperty, NumericProperty

class ListController(EventDispatcher):
    view = ObjectProperty(None)
    items = ListProperty([])
    total = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_controller()
        
    def _setup_controller(self):
        self.bind(
            items=self.view.setter('items'),
            total=self.view.setter('total_price')
        )
        
    def add_item(self, item_data):
        new_item = self._create_item(item_data)
        self.items.append(new_item)
        self._update_total()
