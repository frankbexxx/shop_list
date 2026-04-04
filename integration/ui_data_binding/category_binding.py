from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, ListProperty

class CategoryBinding(EventDispatcher):
    view = ObjectProperty(None)
    model = ObjectProperty(None)
    items = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_bindings()
        
    def _setup_bindings(self):
        self.bind(
            model=self._sync_category_data,
            items=self._update_category_items
        )
