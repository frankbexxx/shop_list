from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    ColorProperty,
    NumericProperty,
    BooleanProperty
)

class CardLayout(BoxLayout):
    background_color = ColorProperty([1, 1, 1, 1])
    elevation = NumericProperty('2dp')
    radius = NumericProperty('8dp')
    has_shadow = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_card()
        
    def _setup_card(self):
        self.orientation = 'vertical'
        self.padding = ('16dp', '16dp')
        self.size_hint_y = None
