from kivy.event import EventDispatcher
from kivy.properties import DictProperty

class Helpers(EventDispatcher):
    utility_functions = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_helpers()
        
    def _setup_helpers(self):
        self.helpers = {
            'array': {
                'sort': self._sort_array,
                'filter': self._filter_array,
                'group': self._group_array
            },
            'string': {
                'capitalize': self._capitalize,
                'slugify': self._slugify,
                'truncate': self._truncate
            },
            'math': {
                'round': self._round_number,
                'calculate_discount': self._calculate_discount,
                'sum_array': self._sum_array
            }
        }
