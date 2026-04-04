from kivy.event import EventDispatcher
from kivy.properties import DictProperty, NumericProperty
from datetime import datetime, timedelta

class CacheManager(EventDispatcher):
    cache = DictProperty({})
    cache_size = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_cache()
        
    def _setup_cache(self):
        self.cache_types = {
            'memory': {'max_size': 100, 'ttl': 3600},
            'disk': {'max_size': 1000, 'ttl': 86400},
            'session': {'max_size': 50, 'ttl': None}
        }
        
    def set_cache(self, key, value, cache_type='memory'):
        if cache_type in self.cache_types:
            self.cache[key] = {
                'value': value,
                'type': cache_type,
                'timestamp': datetime.now()
            }
