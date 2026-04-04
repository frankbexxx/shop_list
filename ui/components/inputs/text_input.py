from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, ColorProperty, BooleanProperty

class CustomTextInput(TextInput):
    hint_text_color = ColorProperty([0.5, 0.5, 0.5, 1])
    border_color = ColorProperty([0.129, 0.588, 0.953, 1])
    has_error = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_input()
        
    def _setup_input(self):
        self.size_hint = (None, None)
        self.height = '48dp'
        self.padding = ('12dp', '8dp')
        self.font_size = '16sp'
        self.multiline = False
        self.background_normal = ''
