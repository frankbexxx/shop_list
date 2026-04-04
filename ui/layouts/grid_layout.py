from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, ColorProperty

class CustomGridLayout(GridLayout):
    spacing_x = NumericProperty('8dp')
    spacing_y = NumericProperty('8dp')
    background_color = ColorProperty([1, 1, 1, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        self.cols = 2
        self.padding = ('16dp', '16dp')
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
