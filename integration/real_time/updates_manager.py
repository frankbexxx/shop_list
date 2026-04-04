from kivy.event import EventDispatcher
from kivy.properties import DictProperty, BooleanProperty
from kivy.clock import Clock

class UpdatesManager(EventDispatcher):
    active_updates = DictProperty({})
    is_monitoring = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_manager()
        
    def _setup_manager(self):
        self.update_interval = 1.0  # seconds
        Clock.schedule_interval(self._check_updates, self.update_interval)
