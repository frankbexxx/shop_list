from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, DictProperty
from kivy.metrics import dp

class FamilyScreen(Screen):
    family_members = ListProperty([])
    shared_lists = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main container
        self.layout = BoxLayout(orientation='vertical')
        
        # Family sharing manager
        self.family_sharing = FamilySharing()
        
        # Shared lists view
        self.shared_lists_view = SharedListsView()
        
        # Activity feed
        self.activity_feed = ActivityFeed()
        
        # Collaboration tools
        self.collab_tools = CollaborationTools()
        
        # Add components
        self.layout.add_widget(self.family_sharing)
        self.layout.add_widget(self.shared_lists_view)
        self.layout.add_widget(self.activity_feed)
        self.layout.add_widget(self.collab_tools)
        
        self.add_widget(self.layout)
