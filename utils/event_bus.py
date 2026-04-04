from kivy.event import EventDispatcher
from kivy.properties import DictProperty
from functools import partial

class EventBus(EventDispatcher):
    subscribers = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_events()
        
    def _initialize_events(self):
        self.events = {
            'list_updated': [],
            'item_added': [],
            'category_changed': [],
            'budget_updated': [],
            'settings_changed': []
        }
        
    def subscribe(self, event_name, callback):
        if event_name in self.events:
            self.events[event_name].append(callback)
            
    def publish(self, event_name, data=None):
        if event_name in self.events:
            for callback in self.events[event_name]:
                if data:
                    callback(data)
                else:
                    callback()
