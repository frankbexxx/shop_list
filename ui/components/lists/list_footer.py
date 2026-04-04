from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    StringProperty, 
    NumericProperty, 
    ColorProperty
)

class ListFooter(BoxLayout):
    total_items = NumericProperty(0)
    total_price = NumericProperty(0)
    currency = StringProperty('$')
    footer_color = ColorProperty([0.95, 0.95, 0.95, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_footer()
        
    def _setup_footer(self):
        self.orientation = 'horizontal'
        self.padding = ('16dp', '8dp')
        self.spacing = '16dp'
        self.size_hint_y = None
        self.height = '56dp'
