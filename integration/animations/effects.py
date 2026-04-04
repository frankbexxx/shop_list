from kivy.event import EventDispatcher
from kivy.properties import DictProperty
from kivy.animation import Animation

class EffectsManager(EventDispatcher):
    effects = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_effects()
        
    def _setup_effects(self):
        self.effects = {
            'ripple': self._create_ripple_effect,
            'bounce': self._create_bounce_effect,
            'pulse': self._create_pulse_effect
        }
