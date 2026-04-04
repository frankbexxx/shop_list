from base_controller import BaseController
from kivy.properties import ObjectProperty, DictProperty

class UserController(BaseController):
    current_user = ObjectProperty(None)
    user_preferences = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_user_controller()
        
    def _setup_user_controller(self):
        self.user_actions = {
            'login': self.login_user,
            'logout': self.logout_user,
            'update_profile': self.update_profile,
            'change_preferences': self.change_preferences,
            'sync_data': self.sync_user_data
        }
        
    def login_user(self, credentials):
        if self.validate_credentials(credentials):
            user = self._authenticate_user(credentials)
            if user:
                self.current_user = user
                return True
        return False
