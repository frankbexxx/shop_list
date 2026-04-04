from kivy.event import EventDispatcher
from kivy.properties import DictProperty, BooleanProperty

class DataService(EventDispatcher):
    data_cache = DictProperty({})
    is_loading = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_data_service()
        
    def _setup_data_service(self):
        self.data_operations = {
            'fetch': self._fetch_data,
            'store': self._store_data,
            'update': self._update_data,
            'delete': self._delete_data,
            'sync': self._sync_data
        }
        
    def execute_operation(self, operation, data):
        if operation in self.data_operations:
            return self.data_operations[operation](data)
