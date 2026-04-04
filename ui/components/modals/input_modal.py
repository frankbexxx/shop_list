from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, ObjectProperty
from ..inputs.text_input import CustomTextInput
from ..buttons.primary_button import PrimaryButton

class InputModal(ModalView):
    title = StringProperty('')
    hint_text = StringProperty('')
    submit_text = StringProperty('Submit')
    on_submit = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_modal()
        
    def _setup_modal(self):
        self.size_hint = (None, None)
        self.size = ('320dp', '280dp')
        self.auto_dismiss = True
        
        self.input_field = CustomTextInput(
            hint_text=self.hint_text,
            size_hint_y=None,
            height='48dp'
        )
