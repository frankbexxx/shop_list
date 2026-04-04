from kivy.event import EventDispatcher
from kivy.properties import DictProperty
from datetime import datetime

class Formatters(EventDispatcher):
    format_rules = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_formatters()
        
    def _setup_formatters(self):
        self.formatters = {
            'currency': self._format_currency,
            'date': self._format_date,
            'number': self._format_number,
            'text': self._format_text,
            'list': self._format_list
        }
        
    def format(self, formatter_type, value, **options):
        if formatter_type in self.formatters:
            return self.formatters[formatter_type](value, **options)
