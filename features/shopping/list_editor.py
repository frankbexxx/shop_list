from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, ListProperty

class ListEditor(EventDispatcher):
    active_list = ObjectProperty(None)
    history = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_editor()
        
    def _setup_editor(self):
        self.operations = {
            'add_item': self._add_item_to_list,
            'remove_item': self._remove_item_from_list,
            'update_item': self._update_item_in_list
        }
