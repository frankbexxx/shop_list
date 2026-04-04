from kivy.event import EventDispatcher
from kivy.properties import DictProperty
from kivy.metrics import dp

class DimensionsManager(EventDispatcher):
    spacing = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_dimensions()
        
    def _setup_dimensions(self):
        self.dimensions = {
            'spacing': {
                'xs': dp(4),
                'sm': dp(8),
                'md': dp(16),
                'lg': dp(24),
                'xl': dp(32)
            },
            'radius': {
                'small': dp(4),
                'medium': dp(8),
                'large': dp(16),
                'round': dp(50)
            }
        }
