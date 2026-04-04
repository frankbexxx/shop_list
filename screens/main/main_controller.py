from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, ListProperty

class MainController(EventDispatcher):
    view = ObjectProperty(None)
    model = ObjectProperty(None)
    active_lists = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_controller()
        
    def _setup_controller(self):
        self.bind(
            active_lists=self.view.setter('lists')
        )
        
    def create_new_list(self, *args):
        new_list = self.model.create_list()
        self.active_lists.append(new_list)
