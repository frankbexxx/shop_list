from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, DictProperty
from kivy.metrics import dp

class FamilySharing(BoxLayout):
    family_members = ListProperty([])
    shared_lists = DictProperty({})
    permissions = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self._setup_sharing()
        
    def _setup_sharing(self):
        # Family members list
        self.members_list = MembersList(
            size_hint_y=0.4
        )
        
        # Shared lists view
        self.lists_view = SharedListsView(
            size_hint_y=0.3
        )
        
        # Permission manager
        self.permission_manager = PermissionManager(
            size_hint_y=0.3
        )
        
        # Invite button
        self.invite_button = InviteButton(
            size_hint_y=None,
            height=dp(48)
        )
        
        self.add_widget(self.members_list)
        self.add_widget(self.lists_view)
        self.add_widget(self.permission_manager)
        self.add_widget(self.invite_button)
