from kivy.event import EventDispatcher
from kivy.properties import DictProperty, BooleanProperty
import json

class StatePersistence(EventDispatcher):
    stored_states = DictProperty({})
    auto_save = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_persistence()
        
    def _setup_persistence(self):
        self.storage_types = {
            'local': self._handle_local_storage,
            'session': self._handle_session_storage,
            'memory': self._handle_memory_storage
        }
        
    def save_state(self, state_id, state_data, storage_type='local'):
        if storage_type in self.storage_types:
            return self.storage_types[storage_type]('save', state_id, state_data)
