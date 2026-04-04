from kivy.event import EventDispatcher
from kivy.properties import ListProperty, BooleanProperty

class StateObserver(EventDispatcher):
    observers = ListProperty([])
    active = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_observers()
        
    def _setup_observers(self):
        self.watch_list = {
            'shopping_lists': [],
            'user_preferences': [],
            'app_settings': [],
            'categories': []
        }
        
    def add_observer(self, key, callback):
        if key in self.watch_list:
            self.watch_list[key].append(callback)
            
    def remove_observer(self, key, callback):
        if key in self.watch_list and callback in self.watch_list[key]:
            self.watch_list[key].remove(callback)
            
    def notify(self, key, data):
        if key in self.watch_list and self.active:
            for callback in self.watch_list[key]:
                callback(data)
