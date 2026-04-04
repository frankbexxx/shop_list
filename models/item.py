from models.base_model import BaseModel
from decimal import Decimal

class Item(BaseModel):
    def __init__(self, name: str, quantity: float = 1.0, unit: str = "units", price: float = 0.0, category: str = "general"):
        super().__init__()
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.price = Decimal(str(price)).quantize(Decimal('0.01'))
        self.category = category
        self.is_purchased = False
        
    def mark_purchased(self):
        self.is_purchased = True
        return self.save()
        
    def calculate_total(self) -> Decimal:
        return (self.price * Decimal(str(self.quantity))).quantize(Decimal('0.01'))
        
    def update(self, name=None, quantity=None, unit=None, price=None, category=None):
        if name: self.name = name
        if quantity: self.quantity = quantity
        if unit: self.unit = unit
        if price: self.price = Decimal(str(price)).quantize(Decimal('0.01'))
        if category: self.category = category
        return self.save()
        
    def to_dict(self):
        base_dict = super().to_dict()
        item_dict = {
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'price': str(self.price),
            'category': self.category,
            'is_purchased': self.is_purchased
        }
        return {**base_dict, **item_dict}
