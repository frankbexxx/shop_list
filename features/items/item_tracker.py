from kivy.event import EventDispatcher
from kivy.properties import DictProperty, BooleanProperty

class ItemTracker(EventDispatcher):
    tracking_data = DictProperty({})
    is_active = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_tracker()
        
    def _setup_tracker(self):
        self.metrics = {
            'popularity': self._track_popularity,
            'price_history': self._track_prices,
            'availability': self._track_availability
        }
