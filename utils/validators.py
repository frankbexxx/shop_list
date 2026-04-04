from kivy.event import EventDispatcher
from kivy.properties import DictProperty

class Validators(EventDispatcher):
    validation_rules = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_validators()
        
    def _setup_validators(self):
        self.validators = {
            'email': self._validate_email,
            'password': self._validate_password,
            'phone': self._validate_phone,
            'price': self._validate_price,
            'quantity': self._validate_quantity
        }
        
    def validate(self, validator_type, value):
        if validator_type in self.validators:
            return self.validators[validator_type](value)
