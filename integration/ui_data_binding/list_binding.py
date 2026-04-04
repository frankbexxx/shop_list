from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

class ListBinding(EventDispatcher):
    view = ObjectProperty(None)
    model = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_bindings()
        
    def _setup_bindings(self):
        self.bind(
            model=self._update_view,
            view=self._update_model
        )
