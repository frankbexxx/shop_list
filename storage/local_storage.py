from kivy.storage.jsonstore import JsonStore
from kivy.event import EventDispatcher

class LocalStorage(EventDispatcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_storage()
        
    def _setup_storage(self):
        self.store = JsonStore('shopping_list_data.json')
        self.cache_duration = 3600  # 1 hour in seconds
