from kivy.event import EventDispatcher
from kivy.properties import DictProperty
from kivy.animation import Animation

class TransitionManager(EventDispatcher):
    transitions = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_transitions()
        
    def _setup_transitions(self):
        self.transitions = {
            'slide': self._create_slide_transition,
            'fade': self._create_fade_transition,
            'scale': self._create_scale_transition
        }
