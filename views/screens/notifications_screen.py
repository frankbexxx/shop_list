from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, BooleanProperty
from kivy.metrics import dp

class NotificationsScreen(Screen):
    notifications = ListProperty([])
    show_read = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main container
        self.layout = BoxLayout(orientation='vertical')
        
        # Notifications list
        self.notifications_list = NotificationsList()
        
        # Filter options
        self.filter_options = NotificationFilters()
        
        # Settings panel
        self.settings_panel = NotificationSettings()
        
        # Quick actions
        self.quick_actions = QuickActions()
        
        # Add components
        self.layout.add_widget(self.notifications_list)
        self.layout.add_widget(self.filter_options)
        self.layout.add_widget(self.settings_panel)
        self.layout.add_widget(self.quick_actions)
        
        self.add_widget(self.layout)
