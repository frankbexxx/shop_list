from kivy.uix.button import Button
from kivy.properties import StringProperty, ColorProperty, NumericProperty

class IconButton(Button):
    icon = StringProperty('')
    icon_color = ColorProperty([0.129, 0.588, 0.953, 1])  # #2196F3
    icon_size = NumericProperty('24dp')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_button()
        
    def _setup_button(self):
        self.size_hint = (None, None)
        self.size = (self.icon_size, self.icon_size)
        self.background_color = [0, 0, 0, 0]
        self.ripple_color = [0.129, 0.588, 0.953, 0.2]
