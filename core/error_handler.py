from kivy.event import EventDispatcher
from kivy.properties import ListProperty, DictProperty

class ErrorHandler(EventDispatcher):
    error_log = ListProperty([])
    error_types = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_error_handler()
        
    def _setup_error_handler(self):
        self.error_types = {
            'validation': self._handle_validation_error,
            'database': self._handle_database_error,
            'network': self._handle_network_error,
            'runtime': self._handle_runtime_error,
            'user': self._handle_user_error
        }
        
    def handle_error(self, error_type, error_data):
        if error_type in self.error_types:
            self.error_types[error_type](error_data)
            self._log_error(error_type, error_data)
