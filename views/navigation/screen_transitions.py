from kivy.uix.screenmanager import (
    NoTransition,
    SlideTransition,
    CardTransition,
    SwapTransition,
    FadeTransition
)
from kivy.properties import ObjectProperty

class ScreenTransitions:
    transition_map = {
        'none': NoTransition,
        'slide': SlideTransition,
        'card': CardTransition,
        'swap': SwapTransition,
        'fade': FadeTransition
    }
    
    def __init__(self):
        self.current_transition = 'slide'
        
    def get_transition(self, transition_name=None):
        if transition_name and transition_name in self.transition_map:
            return self.transition_map[transition_name]()
        return self.transition_map[self.current_transition]()
        
    def set_default_transition(self, transition_name):
        if transition_name in self.transition_map:
            self.current_transition = transition_name
