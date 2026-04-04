from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty

class BaseScreen(Screen):
    controller = ObjectProperty(None)
    screen_title = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_screen()
        
    def _setup_screen(self):
        self.padding = ('16dp', '16dp')
        self.spacing = '8dp'
        
    def on_enter(self):
        """Called when screen enters the view"""
        self.controller.on_screen_enter()
        
    def on_leave(self):
        """Called when screen leaves the view"""
        self.controller.on_screen_leave()
