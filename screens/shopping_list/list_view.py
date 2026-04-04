from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, ListProperty, NumericProperty
from ui.components.lists.list_header import ListHeader
from ui.components.lists.list_footer import ListFooter

class ListView(BoxLayout):
    controller = ObjectProperty(None)
    items = ListProperty([])
    total_price = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_view()
        
    def _setup_view(self):
        self.orientation = 'vertical'
        self.spacing = '8dp'
        
        self.header = ListHeader(
            title='My Shopping List',
            show_action_button=True
        )
