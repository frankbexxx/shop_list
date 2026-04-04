from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.metrics import dp

class VoiceInputHandler(BoxLayout):
    status = StringProperty('ready')
    is_listening = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(56)
        self._setup_interface()
        
    def _setup_interface(self):
        # Microphone button
        self.mic_button = IconButton(
            icon='microphone',
            size_hint_x=None,
            width=dp(56)
        )
        self.mic_button.bind(on_release=self.toggle_listening)
        
        # Status display
        self.status_label = Label(
            text='Tap to speak'
        )
        
        # Animation widget
        self.wave_display = AudioWaveform(
            size_hint_x=0.7
        )
        
        self.add_widget(self.mic_button)
        self.add_widget(self.wave_display)
        self.add_widget(self.status_label)
