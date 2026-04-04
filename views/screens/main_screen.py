from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.metrics import dp

class MainScreen(Screen):
    screen_manager = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main layout container
        self.layout = BoxLayout(orientation='vertical')
        
        # Top bar with status
        self.status_bar = StatusBar()
        
        # Main content area
        self.content_area = BoxLayout()
        
        # Bottom navigation
        self.nav_bar = NavigationBar()
        
        # Add all components
        self.layout.add_widget(self.status_bar)
        self.layout.add_widget(self.content_area)
        self.layout.add_widget(self.nav_bar)
        
        self.add_widget(self.layout)
