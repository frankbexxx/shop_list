from kivy.event import EventDispatcher
from kivy.properties import DictProperty, ListProperty

class AnalyticsService(EventDispatcher):
    metrics = DictProperty({})
    events = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_analytics_service()
        
    def _setup_analytics_service(self):
        self.tracking_types = {
            'user_action': self._track_user_action,
            'performance': self._track_performance,
            'error': self._track_error,
            'usage': self._track_usage
        }
        
    def track_event(self, event_type, event_data):
        if event_type in self.tracking_types:
            return self.tracking_types[event_type](event_data)
