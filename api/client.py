from kivy.event import EventDispatcher
from endpoints.lists import ListEndpoints
from endpoints.users import UserEndpoints

class APIClient(EventDispatcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_client()
        
    def _setup_client(self):
        self.lists = ListEndpoints()
        self.users = UserEndpoints()
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
