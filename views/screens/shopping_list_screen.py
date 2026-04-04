from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty
from kivy.metrics import dp

class ShoppingListScreen(Screen):
    active_lists = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main container
        self.layout = BoxLayout(orientation='vertical')
        
        # List header with search
        self.header = ListHeader()
        
        # Main list view
        self.list_view = SwipeableListView()
        
        # Action buttons
        self.action_bar = QuickActionBar()
        
        # Floating action button
        self.fab = FloatingActionButton()
        
        # Add components
        self.layout.add_widget(self.header)
        self.layout.add_widget(self.list_view)
        self.layout.add_widget(self.action_bar)
        self.layout.add_widget(self.fab)
        
        self.add_widget(self.layout)
