from datetime import datetime
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ObjectProperty

class BaseModel(EventDispatcher):
    id = StringProperty('')
    created_at = ObjectProperty(None)
    updated_at = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_model()
        
    def _setup_model(self):
        if not self.id:
            self.id = self._generate_id()
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
