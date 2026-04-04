from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty

class Navigation(BoxLayout):
    current_screen = StringProperty('')
    nav_items = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_navigation()
        
    def _setup_navigation(self):
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = '56dp'
        
        self.nav_items = [
            {'name': 'main', 'icon': 'home', 'text': 'Home'},
            {'name': 'shopping_list', 'icon': 'list', 'text': 'Lists'},
            {'name': 'categories', 'icon': 'category', 'text': 'Categories'},
            {'name': 'settings', 'icon': 'settings', 'text': 'Settings'}
        ]
