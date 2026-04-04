from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

class BaseController(EventDispatcher):
    db_manager = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_controller()
        
    def _setup_controller(self):
        self.actions = {
            'create': self._create,
            'read': self._read,
            'update': self._update,
            'delete': self._delete
        }
        
    def execute_action(self, action_type, data):
        if action_type in self.actions:
            return self.actions[action_type](data)
        return False
        
    def validate_data(self, data):
        return True
