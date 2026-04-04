from kivy.event import EventDispatcher
from kivy.properties import ListProperty

class SignalHandler(EventDispatcher):
    active_signals = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_signals()
        
    def _setup_signals(self):
        self.signals = {
            'data_changed': [],
            'state_updated': [],
            'sync_required': [],
            'refresh_needed': []
        }
        
    def emit(self, signal_name, data=None):
        if signal_name in self.signals:
            for handler in self.signals[signal_name]:
                handler(data)
                
    def connect(self, signal_name, handler):
        if signal_name in self.signals:
            self.signals[signal_name].append(handler)
            
    def disconnect(self, signal_name, handler):
        if signal_name in self.signals:
            self.signals[signal_name].remove(handler)
