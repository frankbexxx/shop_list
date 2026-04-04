from kivy.event import EventDispatcher
from kivy.properties import DictProperty, ListProperty

class StateStore(EventDispatcher):
    store = DictProperty({})
    history = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_store()
        
    def _setup_store(self):
        self.store = {
            'app': {
                'theme': 'light',
                'language': 'en',
                'notifications_enabled': True
            },
            'user': {
                'preferences': {},
                'recent_lists': [],
                'favorites': []
            },
            'data': {
                'lists': {},
                'items': {},
                'categories': {}
            }
        }
        
    def commit(self, path, value):
        keys = path.split('.')
        current = self.store
        for key in keys[:-1]:
            current = current[key]
        current[keys[-1]] = value
        self._save_to_history()
        
    def _save_to_history(self):
        self.history.append(self.store.copy())
