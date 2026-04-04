from kivy.event import EventDispatcher
from kivy.properties import DictProperty, BooleanProperty

class CategoryOrganizer(EventDispatcher):
    hierarchy = DictProperty({})
    is_sorting = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_organizer()
        
    def _setup_organizer(self):
        self.sort_methods = {
            'alphabetical': self._sort_alphabetically,
            'usage': self._sort_by_usage,
            'custom': self._sort_custom_order
        }
