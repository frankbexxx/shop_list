from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

class CRUDService(EventDispatcher):
    db_manager = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_service()
        
    def _setup_service(self):
        self.operations = {
            'create': self._create_record,
            'read': self._read_record,
            'update': self._update_record,
            'delete': self._delete_record
        }
