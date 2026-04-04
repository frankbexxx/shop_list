from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    StringProperty, 
    BooleanProperty, 
    NumericProperty,
    ObjectProperty
)

class ListItem(BoxLayout):
    title = StringProperty('')
    subtitle = StringProperty('')
    is_selected = BooleanProperty(False)
    item_id = StringProperty('')
    on_select = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_item()
        
    def _setup_item(self):
        self.orientation = 'horizontal'
        self.padding = ('16dp', '8dp')
        self.spacing = '8dp'
        self.size_hint_y = None
        self.height = '72dp'
