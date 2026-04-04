from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty
from kivy.metrics import dp

class ShoppingListShare(BoxLayout):
    shared_users = ListProperty([])
    share_link = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self.padding = dp(10)
        self._setup_share_interface()
        
    def _setup_share_interface(self):
        # Share link generator
        self.link_box = ShareLinkBox(
            size_hint_y=None,
            height=dp(50)
        )
        
        # User permissions grid
        self.permissions_grid = PermissionsGrid(
            size_hint_y=None,
            height=dp(200)
        )
        
        # Quick share buttons
        self.share_buttons = QuickShareBar(
            size_hint_y=None,
            height=dp(48)
        )
        
        self.add_widget(self.link_box)
        self.add_widget(self.permissions_grid)
        self.add_widget(self.share_buttons)
