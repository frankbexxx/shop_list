from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, ObjectProperty
from ..buttons.primary_button import PrimaryButton
from ..buttons.secondary_button import SecondaryButton

class ConfirmModal(ModalView):
    title = StringProperty('')
    message = StringProperty('')
    confirm_text = StringProperty('Confirm')
    cancel_text = StringProperty('Cancel')
    on_confirm = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_modal()
        
    def _setup_modal(self):
        self.size_hint = (None, None)
        self.size = ('320dp', '240dp')
        self.auto_dismiss = False
        self.background_color = [0, 0, 0, 0.5]
