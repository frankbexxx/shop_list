from kivy.event import EventDispatcher
from kivy.properties import DictProperty

class ValidationService(EventDispatcher):
    validation_rules = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_validation()
        
    def _setup_validation(self):
        self.rules = {
            'required': self._validate_required,
            'email': self._validate_email,
            'min_length': self._validate_min_length,
            'max_length': self._validate_max_length,
            'numeric': self._validate_numeric
        }
