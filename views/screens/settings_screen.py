from kivy.uix.screenmanager import Screen
from kivy.properties import DictProperty, BooleanProperty
from kivy.metrics import dp

class SettingsScreen(Screen):
    app_settings = DictProperty({})
    notifications_enabled = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main container
        self.layout = BoxLayout(orientation='vertical')
        
        # Theme selector
        self.theme_selector = ColorThemeSelector()
        
        # Notification settings
        self.notification_settings = NotificationSettings()
        
        # Language selector
        self.language_selector = LanguageSelector()
        
        # Data management
        self.data_manager = DataManagement()
        
        # Add components
        self.layout.add_widget(self.theme_selector)
        self.layout.add_widget(self.notification_settings)
        self.layout.add_widget(self.language_selector)
        self.layout.add_widget(self.data_manager)
        
        self.add_widget(self.layout)
