from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    StringProperty, 
    NumericProperty, 
    ColorProperty,
    OptionProperty
)

class FlexLayout(BoxLayout):
    direction = OptionProperty('row', options=['row', 'column'])
    justify_content = StringProperty('flex-start')
    align_items = StringProperty('stretch')
    gap = NumericProperty('8dp')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        self.orientation = 'horizontal' if self.direction == 'row' else 'vertical'
        self.padding = ('16dp', '16dp')
        self.spacing = self.gap
