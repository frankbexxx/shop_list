from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, DictProperty

class StateSynchronizer(EventDispatcher):
    is_syncing = BooleanProperty(False)
    sync_queue = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_synchronizer()
        
    def _setup_synchronizer(self):
        self.sync_targets = {
            'screens': {},
            'widgets': {},
            'models': {},
            'controllers': {}
        }
        
    def register_sync_target(self, target_type, target_id, target_instance):
        if target_type in self.sync_targets:
            self.sync_targets[target_type][target_id] = target_instance
            self.sync_state(target_type, target_id)
