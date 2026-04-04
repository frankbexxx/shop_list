from kivy.event import EventDispatcher
from kivy.properties import DictProperty, BooleanProperty

class DataBinding(EventDispatcher):
    bindings = DictProperty({})
    active = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_bindings()
        
    def _initialize_bindings(self):
        self.binding_types = {
            'one_way': self._bind_one_way,
            'two_way': self._bind_two_way,
            'one_time': self._bind_one_time
        }
        
    def bind_property(self, source, target, binding_type='two_way'):
        if binding_type in self.binding_types:
            binding_id = f"{id(source)}_{id(target)}"
            self.bindings[binding_id] = {
                'source': source,
                'target': target,
                'type': binding_type
            }
            self.binding_types[binding_type](source, target)
            
    def unbind_property(self, source, target):
        binding_id = f"{id(source)}_{id(target)}"
        if binding_id in self.bindings:
            self.bindings.pop(binding_id)
