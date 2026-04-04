from kivy.event import EventDispatcher
from kivy.properties import ListProperty, NumericProperty

class ItemManager(EventDispatcher):
    items = ListProperty([])
    total_count = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_manager()
        
    def _setup_manager(self):
        self.operations = {
            'add': self._add_item,
            'remove': self._remove_item,
            'update': self._update_item,
            'search': self._search_items
        }
