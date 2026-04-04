from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, BoundedNumericProperty
from ..buttons.icon_button import IconButton
from .text_input import CustomTextInput

class NumberInput(BoxLayout):
    value = BoundedNumericProperty(0, min=0)
    step = NumericProperty(1)
    max_value = NumericProperty(999)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_number_input()
        
    def _setup_number_input(self):
        self.orientation = 'horizontal'
        self.spacing = '8dp'
        
        self.decrease_button = IconButton(
            icon='minus',
            on_press=self.decrease_value
        )
        
        self.input_field = CustomTextInput(
            text=str(self.value),
            input_filter='int'
        )
