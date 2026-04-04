from kivy.event import EventDispatcher
from kivy.properties import DictProperty
from datetime import datetime

class Logger(EventDispatcher):
    log_entries = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_logger()
        
    def _setup_logger(self):
        self.log_levels = {
            'debug': self._log_debug,
            'info': self._log_info,
            'warning': self._log_warning,
            'error': self._log_error,
            'critical': self._log_critical
        }
        
    def log(self, level, message, context=None):
        timestamp = datetime.now().isoformat()
        if level in self.log_levels:
            self.log_levels[level](timestamp, message, context)
