from kivy.event import EventDispatcher
from kivy.properties import ListProperty, DictProperty

class CategoryManager(EventDispatcher):
    categories = ListProperty([])
    category_map = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_manager()
        
    def _setup_manager(self):
        self.operations = {
            'create': self._create_category,
            'update': self._update_category,
            'delete': self._delete_category
        }
