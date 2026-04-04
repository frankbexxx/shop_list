from kivy.app import App
from kivy.properties import ObjectProperty
from app_config import AppConfig
from app_builder import AppBuilder

class ShoppingApp(App):
    config = ObjectProperty(None)
    builder = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_app()
        
    def _setup_app(self):
        self.config = AppConfig()
        self.builder = AppBuilder()
        
    def build(self):
        return self.builder.build_app()
        
    def on_start(self):
        self.config.load_settings()
        
    def on_stop(self):
        self.config.save_settings()
