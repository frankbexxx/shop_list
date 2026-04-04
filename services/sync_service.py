from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, ListProperty

class SyncService(EventDispatcher):
    is_syncing = BooleanProperty(False)
    sync_queue = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_sync_service()
        
    def _setup_sync_service(self):
        self.sync_types = {
            'full': self._full_sync,
            'incremental': self._incremental_sync,
            'selective': self._selective_sync,
            'background': self._background_sync
        }
        
    def start_sync(self, sync_type='incremental', data=None):
        if sync_type in self.sync_types:
            return self.sync_types[sync_type](data)
