from models.base_model import BaseModel
from models.item import Item
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

class ShoppingList(BaseModel):
    def __init__(self, name: str, owner_id: str):
        super().__init__()
        self.name = name
        self.owner_id = owner_id
        self.items: List[Item] = []
        self.category = "default"
        self.is_active = True
        
    def add_item(self, item: Item) -> bool:
        self.items.append(item)
        return self.save()
        
    def remove_item(self, item_id: str) -> bool:
        self.items = [item for item in self.items if item.id != item_id]
        return self.save()
        
    def get_total(self) -> Decimal:
        return sum(item.calculate_total() for item in self.items)
        
    def sort_items(self, key: str = 'name', reverse: bool = False) -> List[Item]:
        return sorted(self.items, key=lambda x: getattr(x, key), reverse=reverse)
        
    def filter_items(self, **kwargs) -> List[Item]:
        filtered_items = self.items
        for key, value in kwargs.items():
            filtered_items = [item for item in filtered_items 
                            if getattr(item, key) == value]
        return filtered_items
        
    def mark_complete(self) -> bool:
        self.is_active = False
        return self.save()
        
    def to_dict(self):
        base_dict = super().to_dict()
        list_dict = {
            'name': self.name,
            'owner_id': self.owner_id,
            'items': [item.to_dict() for item in self.items],
            'category': self.category,
            'is_active': self.is_active
        }
        return {**base_dict, **list_dict}
