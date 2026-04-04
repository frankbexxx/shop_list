from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, ListProperty

class CategoriesController(EventDispatcher):
    view = ObjectProperty(None)
    categories = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_controller()
        
    def _setup_controller(self):
        self.bind(
            categories=self.view.setter('categories')
        )
        
    def create_category(self, *args):
        new_category = self.model.create_category()
        self.categories.append(new_category)
