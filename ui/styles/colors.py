from kivy.event import EventDispatcher
from kivy.properties import DictProperty

class ColorManager(EventDispatcher):
    color_palette = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_colors()
        
    def _setup_colors(self):
        self.colors = {
            'primary': {
                'main': '#2196F3',
                'light': '#64B5F6',
                'dark': '#1976D2',
                'contrast': '#FFFFFF'
            },
            'secondary': {
                'main': '#FF4081',
                'light': '#FF80AB',
                'dark': '#C51162',
                'contrast': '#FFFFFF'
            },
            'success': {
                'main': '#4CAF50',
                'light': '#81C784',
                'dark': '#388E3C',
                'contrast': '#FFFFFF'
            }
        }
