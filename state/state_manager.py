from kivy.event import EventDispatcher
from kivy.properties import DictProperty, BooleanProperty

class StateManager(EventDispatcher):
    state = DictProperty({})
    is_initialized = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_state()
        
    def _initialize_state(self):
        self.state = {
            'shopping_lists': [],
            'categories': {},
            'current_user': None,
            'settings': {},
            'notifications': []
        }
        self.is_initialized = True
        
    def update_state(self, key, value):
        if key in self.state:
            self.state[key] = value
            self.dispatch('on_state_changed', key, value)
            
    def get_state(self, key):
        return self.state.get(key)
        
    def reset_state(self):
        self._initialize_state()
