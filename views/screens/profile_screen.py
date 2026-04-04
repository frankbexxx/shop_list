from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, DictProperty
from kivy.metrics import dp

class ProfileScreen(Screen):
    user_data = DictProperty({})
    profile_image = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main container
        self.layout = BoxLayout(orientation='vertical')
        
        # Profile header
        self.profile_header = ProfileHeader()
        
        # User preferences
        self.preferences = UserPreferences()
        
        # Shopping history
        self.history = ShoppingHistory()
        
        # Account settings
        self.account_settings = AccountSettings()
        
        # Add components
        self.layout.add_widget(self.profile_header)
        self.layout.add_widget(self.preferences)
        self.layout.add_widget(self.history)
        self.layout.add_widget(self.account_settings)
        
        self.add_widget(self.layout)
