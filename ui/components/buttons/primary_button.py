from kivy.uix.button import Button
from kivy.properties import StringProperty, ColorProperty

class PrimaryButton(Button):
    text_color = ColorProperty([1, 1, 1, 1])
    background_color = ColorProperty([0.129, 0.588, 0.953, 1])  # #2196F3
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_button()
        
    def _setup_button(self):
        self.size_hint = (None, None)
        self.height = '48dp'
        self.padding = ('16dp', '8dp')
        self.font_size = '16sp'
        
    def on_press(self):
        self.opacity = 0.8
        
    def on_release(self):
        self.opacity = 1.0
