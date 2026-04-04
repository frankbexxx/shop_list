from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, StringProperty

class AuthService(EventDispatcher):
    is_authenticated = BooleanProperty(False)
    auth_token = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_auth_service()
        
    def _setup_auth_service(self):
        self.auth_methods = {
            'email': self._authenticate_email,
            'google': self._authenticate_google,
            'facebook': self._authenticate_facebook,
            'apple': self._authenticate_apple
        }
        
    def authenticate(self, method, credentials):
        if method in self.auth_methods:
            return self.auth_methods[method](credentials)
