from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, BooleanProperty

class AppManager(EventDispatcher):
    is_initialized = BooleanProperty(False)
    current_state = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_managers()
        
    def _setup_managers(self):
        self.managers = {
            'settings': SettingsManager(),
            'resources': ResourceManager(),
            'errors': ErrorHandler(),
            'logger': Logger(),
            'cache': CacheManager()
        }
        
    def initialize_app(self):
        for manager in self.managers.values():
            manager.initialize()
        self.is_initialized = True
