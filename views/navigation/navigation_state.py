from kivy.event import EventDispatcher
from kivy.properties import DictProperty, BooleanProperty

class NavigationState(EventDispatcher):
    state = DictProperty({
        'can_go_back': False,
        'previous_route': None,
        'next_route': None,
        'params': {}
    })
    
    is_navigating = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_state()
        
    def _initialize_state(self):
        self.navigation_stack = []
        self.current_index = -1
        
    def push_state(self, route, params=None):
        self.is_navigating = True
        self.current_index += 1
        self.navigation_stack.append({
            'route': route,
            'params': params or {}
        })
        self._update_state()
        
    def pop_state(self):
        if self.can_go_back():
            self.is_navigating = True
            self.navigation_stack.pop()
            self.current_index -= 1
            self._update_state()
            return True
        return False
        
    def _update_state(self):
        self.state.update({
            'can_go_back': self.can_go_back(),
            'previous_route': self.get_previous_route(),
            'next_route': self.get_next_route(),
            'params': self.get_current_params()
        })
        self.is_navigating = False
