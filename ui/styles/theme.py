from kivy.event import EventDispatcher
from kivy.properties import DictProperty, StringProperty

class ThemeManager(EventDispatcher):
    current_theme = StringProperty('light')
    theme_data = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_themes()
        
    def _setup_themes(self):
        self.themes = {
            'light': {
                'background': '#FFFFFF',
                'surface': '#F5F5F5',
                'primary': '#2196F3',
                'secondary': '#FF4081',
                'text': '#212121'
            },
            'dark': {
                'background': '#121212',
                'surface': '#1E1E1E',
                'primary': '#BB86FC',
                'secondary': '#03DAC6',
                'text': '#FFFFFF'
            }
        }
