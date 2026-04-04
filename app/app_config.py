from kivy.event import EventDispatcher
from kivy.properties import DictProperty
import json
import os

class AppConfig(EventDispatcher):
    settings = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_config()
        
    def _setup_config(self):
        self.config_files = {
            'settings': 'config/settings.json',
            'routes': 'config/routes.json',
            'theme': 'config/theme.json'
        }
        
    def load_settings(self):
        for config_type, file_path in self.config_files.items():
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    self.settings[config_type] = json.load(f)
