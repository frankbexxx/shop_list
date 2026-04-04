from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, NumericProperty
from kivy.network.urlrequest import UrlRequest

class SyncService(EventDispatcher):
    is_syncing = BooleanProperty(False)
    sync_progress = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_service()
        
    def _setup_service(self):
        self.sync_queue = []
        self.retry_attempts = 3
