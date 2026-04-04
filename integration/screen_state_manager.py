from kivy.event import EventDispatcher
from kivy.properties import DictProperty, ObjectProperty

class ScreenStateManager(EventDispatcher):
    screen_states = DictProperty({})
    active_screen = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_screen_states()
        
    def _setup_screen_states(self):
        self.states = {
            'main': {'widgets': [], 'data': {}},
            'shopping_list': {'widgets': [], 'data': {}},
            'category': {'widgets': [], 'data': {}},
            'settings': {'widgets': [], 'data': {}}
        }
        
    def register_screen(self, screen_name, screen_instance):
        if screen_name in self.states:
            self.states[screen_name]['instance'] = screen_instance
            self.sync_screen_state(screen_name)
