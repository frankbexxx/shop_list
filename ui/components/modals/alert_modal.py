from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, ColorProperty
from ..buttons.primary_button import PrimaryButton

class AlertModal(ModalView):
    title = StringProperty('')
    message = StringProperty('')
    button_text = StringProperty('OK')
    modal_color = ColorProperty([1, 1, 1, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_modal()
        
    def _setup_modal(self):
        self.size_hint = (None, None)
        self.size = ('300dp', '200dp')
        self.auto_dismiss = True
        self.background_color = [0, 0, 0, 0.5]
