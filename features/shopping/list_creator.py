from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, BooleanProperty

class ListCreator(EventDispatcher):
    model = ObjectProperty(None)
    is_creating = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_creator()
        
    def _setup_creator(self):
        self.templates = {
            'basic': self._create_basic_list,
            'detailed': self._create_detailed_list,
            'categorized': self._create_categorized_list
        }
