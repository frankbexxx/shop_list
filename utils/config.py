from kivy.event import EventDispatcher
from kivy.properties import DictProperty

class Config(EventDispatcher):
    config_data = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_config()
        
    def _setup_config(self):
        self.config = {
            'app': {
                'debug': True,
                'api_url': 'https://api.shoppinglist.com',
                'max_items': 1000,
                'cache_duration': 3600
            },
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'shopping_list_db'
            },
            'features': {
                'offline_mode': True,
                'cloud_sync': True,
                'notifications': True
            }
        }
