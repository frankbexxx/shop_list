from kivy.event import EventDispatcher
from kivy.properties import DictProperty, ListProperty

class ResourceManager(EventDispatcher):
    resources = DictProperty({})
    loaded_assets = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_resources()
        
    def _setup_resources(self):
        self.resource_types = {
            'images': {
                'path': 'assets/images/',
                'extensions': ['.png', '.jpg', '.webp']
            },
            'icons': {
                'path': 'assets/icons/',
                'extensions': ['.png', '.svg']
            },
            'fonts': {
                'path': 'assets/fonts/',
                'extensions': ['.ttf', '.otf']
            },
            'data': {
                'path': 'assets/data/',
                'extensions': ['.json', '.yaml']
            }
        }
