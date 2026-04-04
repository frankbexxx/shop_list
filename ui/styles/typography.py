from kivy.event import EventDispatcher
from kivy.properties import DictProperty

class TypographyManager(EventDispatcher):
    font_styles = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_typography()
        
    def _setup_typography(self):
        self.typography = {
            'h1': {
                'font_size': 96,
                'font_weight': 'light',
                'line_height': 1.167,
                'letter_spacing': -1.5
            },
            'h2': {
                'font_size': 60,
                'font_weight': 'light',
                'line_height': 1.2,
                'letter_spacing': -0.5
            },
            'body1': {
                'font_size': 16,
                'font_weight': 'regular',
                'line_height': 1.5,
                'letter_spacing': 0.15
            }
        }
