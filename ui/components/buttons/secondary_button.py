from kivy.uix.button import Button
from kivy.properties import StringProperty, ColorProperty

class SecondaryButton(Button):
    text_color = ColorProperty([0.129, 0.588, 0.953, 1])  # #2196F3
    background_color = ColorProperty([0.95, 0.95, 0.95, 1])  # #F5F5F5
    border_color = ColorProperty([0.129, 0.588, 0.953, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_button()
        
    def _setup_button(self):
        self.size_hint = (None, None)
        self.height = '48dp'
        self.padding = ('16dp', '8dp')
        self.font_size = '16sp'
        self.border_width = '2dp'
