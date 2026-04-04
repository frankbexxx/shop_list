from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import dp

class DialogBox(ModalView):
    title = StringProperty('')
    content = StringProperty('')
    callback = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, None)
        self.height = dp(200)
        self.auto_dismiss = False
        
        self.layout = BoxLayout(orientation='vertical', padding=dp(16))
        
        # Title
        self.title_label = Label(
            text=self.title,
            size_hint_y=0.2,
            bold=True
        )
        
        # Content
        self.content_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=0.6
        )
        
        # Buttons
        self.button_layout = BoxLayout(
            size_hint_y=0.2,
            spacing=dp(10)
        )
        
        self.cancel_button = Button(
            text='Cancel',
            on_release=self.dismiss
        )
        
        self.confirm_button = Button(
            text='Confirm',
            on_release=self._on_confirm
        )
        
        self._setup_layout()
        
    def _setup_layout(self):
        self.button_layout.add_widget(self.cancel_button)
        self.button_layout.add_widget(self.confirm_button)
        
        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.content_layout)
        self.layout.add_widget(self.button_layout)
        
        self.add_widget(self.layout)
        
    def _on_confirm(self, *args):
        if self.callback:
            self.callback()
        self.dismiss()
