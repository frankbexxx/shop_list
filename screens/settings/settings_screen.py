from common.base_screen import BaseScreen
from kivy.properties import ObjectProperty, DictProperty

class SettingsScreen(BaseScreen):
    view = ObjectProperty(None)
    settings = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_settings_screen()
        
    def _setup_settings_screen(self):
        self.screen_title = 'Settings'
        
    def on_enter(self):
        super().on_enter()
        self.controller.load_settings()
