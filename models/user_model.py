from base_model import BaseModel
from kivy.properties import (
    StringProperty, 
    ListProperty, 
    DictProperty, 
    BooleanProperty
)

class UserModel(BaseModel):
    username = StringProperty('')
    email = StringProperty('')
    preferences = DictProperty({})
    shopping_lists = ListProperty([])
    is_active = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_user()
        
    def _setup_user(self):
        self.preferences = {
            'theme': 'light',
            'language': 'en',
            'notifications': True,
            'currency': 'USD'
        }
        
    def add_shopping_list(self, list_id):
        if list_id not in self.shopping_lists:
            self.shopping_lists.append(list_id)
            
    def remove_shopping_list(self, list_id):
        if list_id in self.shopping_lists:
            self.shopping_lists.remove(list_id)
