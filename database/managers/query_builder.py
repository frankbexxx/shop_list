from kivy.event import EventDispatcher
from kivy.properties import DictProperty

class QueryBuilder(EventDispatcher):
    query_parts = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_builder()
        
    def _setup_builder(self):
        self.query_parts = {
            'select': [],
            'from': '',
            'where': [],
            'order_by': [],
            'limit': None
        }
