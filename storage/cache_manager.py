from kivy.event import EventDispatcher
from kivy.properties import DictProperty
from time import time

class CacheManager(EventDispatcher):
    cache = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_cache()
        
    def _setup_cache(self):
        self.max_size = 100  # maximum items in cache
        self.expiration = 300  # 5 minutes in seconds
