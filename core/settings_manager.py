from kivy.event import EventDispatcher
from kivy.properties import DictProperty, StringProperty

class SettingsManager(EventDispatcher):
    settings = DictProperty({})
    current_locale = StringProperty('en')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_settings()
        
    def _setup_settings(self):
        self.settings = {
            'app': {
                'theme': 'light',
                'language': 'en',
                'currency': 'USD',
                'notifications': True
            },
            'display': {
                'font_size': 'medium',
                'color_scheme': 'default',
                'animations': True
            },
            'storage': {
                'auto_save': True,
                'backup_enabled': True,
                'sync_frequency': 'daily'
            }
        }
