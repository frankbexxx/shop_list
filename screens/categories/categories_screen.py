from common.base_screen import BaseScreen
from kivy.properties import ObjectProperty, ListProperty

class CategoriesScreen(BaseScreen):
    view = ObjectProperty(None)
    categories = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_categories_screen()
        
    def _setup_categories_screen(self):
        self.screen_title = 'Categories'
        
    def on_enter(self):
        super().on_enter()
        self.controller.load_categories()
