from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, DictProperty

class SettingsView(BoxLayout):
    controller = ObjectProperty(None)
    settings_data = DictProperty({
        'app': {
            'theme': 'light',
            'language': 'en',
            'notifications': True
        },
        'display': {
            'font_size': 'medium',
            'color_scheme': 'default'
        },
        'storage': {
            'auto_save': True,
            'backup': True
        }
    })
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_view()
