from kivy.event import EventDispatcher
from kivy.properties import DictProperty, ListProperty

class WidgetStateManager(EventDispatcher):
    widget_states = DictProperty({})
    active_widgets = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_widget_states()
        
    def _setup_widget_states(self):
        self.states = {
            'list_widgets': {},
            'category_widgets': {},
            'input_widgets': {},
            'display_widgets': {}
        }
        
    def register_widget(self, widget_id, widget_instance):
        category = self._get_widget_category(widget_id)
        if category in self.states:
            self.states[category][widget_id] = {
                'instance': widget_instance,
                'state': widget_instance.get_state()
            }
