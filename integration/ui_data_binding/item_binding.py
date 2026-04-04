from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, BooleanProperty

class ItemBinding(EventDispatcher):
    view = ObjectProperty(None)
    model = ObjectProperty(None)
    is_synced = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_bindings()
        
    def _setup_bindings(self):
        self.bind(
            model=self._sync_item_data,
            view=self._handle_item_updates
        )
