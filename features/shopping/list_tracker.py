from kivy.event import EventDispatcher
from kivy.properties import DictProperty, NumericProperty

class ListTracker(EventDispatcher):
    statistics = DictProperty({})
    total_items = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_tracker()
        
    def _setup_tracker(self):
        self.tracking_metrics = {
            'completion': self._track_completion,
            'spending': self._track_spending,
            'frequency': self._track_frequency
        }
