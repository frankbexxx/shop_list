from base_model import BaseModel
from kivy.properties import (
    StringProperty, 
    ListProperty, 
    BooleanProperty
)

class UserModel(BaseModel):
    username = StringProperty('')
    email = StringProperty('')
    lists = ListProperty([])
    settings = ListProperty([])
    is_active = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_user()
        
    def _setup_user(self):
        self.bind(
            lists=self._update_lists_count
        )
