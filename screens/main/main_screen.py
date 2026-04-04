from common.base_screen import BaseScreen
from kivy.properties import ObjectProperty, ListProperty

class MainScreen(BaseScreen):
    view = ObjectProperty(None)
    recent_lists = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_main_screen()
        
    def _setup_main_screen(self):
        self.screen_title = 'Shopping Lists'
        self.recent_lists = []
        
    def on_enter(self):
        super().on_enter()
        self.load_recent_lists()
