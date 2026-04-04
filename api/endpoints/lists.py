from kivy.network.urlrequest import UrlRequest
from kivy.event import EventDispatcher

class ListEndpoints(EventDispatcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'https://api.shoppinglist.com/v1'
        
    def get_lists(self, user_id):
        endpoint = f'{self.base_url}/lists'
        return UrlRequest(
            endpoint,
            method='GET',
            req_headers={'User-Id': user_id}
        )
