from kivy.event import EventDispatcher
from kivy.properties import DictProperty
from kivy.animation import Animation

class AnimationsManager(EventDispatcher):
    animations = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_animations()
        
    def _setup_animations(self):
        self.animation_types = {
            'fade': {
                'in': lambda widget: Animation(opacity=1, duration=0.3),
                'out': lambda widget: Animation(opacity=0, duration=0.3)
            },
            'slide': {
                'in': lambda widget: Animation(x=0, duration=0.3),
                'out': lambda widget: Animation(x=widget.width, duration=0.3)
            },
            'scale': {
                'in': lambda widget: Animation(scale=1, duration=0.3),
                'out': lambda widget: Animation(scale=0, duration=0.3)
            }
        }
