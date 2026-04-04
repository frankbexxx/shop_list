from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty
from screens.common.screen_manager import AppScreenManager
from screens.common.navigation import Navigation

class AppBuilder(EventDispatcher):
    screen_manager = ObjectProperty(None)
    navigation = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_builder()
        
    def _setup_builder(self):
        self.screens = {
            'main': self._build_main_screen,
            'shopping_list': self._build_list_screen,
            'categories': self._build_categories_screen,
            'settings': self._build_settings_screen
        }
