from kivy.event import EventDispatcher
from kivy.properties import DictProperty

class RelationService(EventDispatcher):
    relations = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_relations()
        
    def _setup_relations(self):
        self.relation_types = {
            'one_to_one': self._handle_one_to_one,
            'one_to_many': self._handle_one_to_many,
            'many_to_many': self._handle_many_to_many
        }
