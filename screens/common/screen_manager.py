from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty, DictProperty

class AppScreenManager(ScreenManager):
    active_controllers = DictProperty({})
    navigation = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_manager()
        
    def _setup_manager(self):
        self.transition.duration = 0.3
        
    def switch_screen(self, screen_name):
        if screen_name in self.screen_names:
            self.current = screen_name
            self.navigation.current_screen = screen_name
