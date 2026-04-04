from kivy.network.urlrequest import UrlRequest
from kivy.event import EventDispatcher

class UserEndpoints(EventDispatcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'https://api.shoppinglist.com/v1'
        
    def get_user_profile(self, user_id):
        endpoint = f'{self.base_url}/users/{user_id}'
        return UrlRequest(
            endpoint,
            method='GET',
            req_headers={'Authorization': self._get_auth_token()}
        )
