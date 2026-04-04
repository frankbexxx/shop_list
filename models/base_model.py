from kivy.event import EventDispatcher
from kivy.properties import StringProperty, DictProperty
from datetime import datetime

class BaseModel(EventDispatcher):
    id = StringProperty('')
    created_at = StringProperty('')
    updated_at = StringProperty('')
    metadata = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_model()
        
    def _initialize_model(self):
        if not self.id:
            self.id = self._generate_id()
        if not self.created_at:
            self.created_at = self._get_timestamp()
            
    def _generate_id(self):
        return f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
    def _get_timestamp(self):
        return datetime.now().isoformat()
        
    def update(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = self._get_timestamp()
