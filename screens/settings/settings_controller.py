from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, DictProperty

class SettingsController(EventDispatcher):
    view = ObjectProperty(None)
    settings = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_controller()
        
    def _setup_controller(self):
        self.bind(
            settings=self.view.setter('settings_data')
        )
        
    def update_setting(self, category, key, value):
        if category in self.settings:
            self.settings[category][key] = value
            self._save_settings()
