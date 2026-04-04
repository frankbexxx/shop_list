from models.base_model import BaseModel
from models.shopping_list import ShoppingList
from typing import List, Optional
import hashlib
import json

class User(BaseModel):
    def __init__(self, username: str, email: str):
        super().__init__()
        self.username = username
        self.email = email
        self.password_hash = None
        self.lists: List[ShoppingList] = []
        self.preferences = {
            'default_sort': 'name',
            'theme': 'light',
            'notifications': True
        }
        
    def set_password(self, password: str):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        return self.save()
        
    def verify_password(self, password: str) -> bool:
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
        
    def create_list(self, name: str) -> ShoppingList:
        new_list = ShoppingList(name, self.id)
        self.lists.append(new_list)
        self.save()
        return new_list
        
    def get_lists(self, active_only: bool = True) -> List[ShoppingList]:
        if active_only:
            return [lst for lst in self.lists if lst.is_active]
        return self.lists
        
    def delete_list(self, list_id: str) -> bool:
        self.lists = [lst for lst in self.lists if lst.id != list_id]
        return self.save()
        
    def update_preferences(self, **kwargs):
        self.preferences.update(kwargs)
        return self.save()
        
    def to_dict(self):
        base_dict = super().to_dict()
        user_dict = {
            'username': self.username,
            'email': self.email,
            'lists': [lst.to_dict() for lst in self.lists],
            'preferences': self.preferences
        }
        return {**base_dict, **user_dict}
