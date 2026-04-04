from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock

class BarcodeScanner(BoxLayout):
    scan_result = StringProperty('')
    camera_active = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self._setup_scanner()
        
    def _setup_scanner(self):
        # Camera preview
        self.preview = CameraPreview(
            size_hint_y=0.7
        )
        
        # Scan overlay
        self.overlay = ScanOverlay(
            size_hint_y=0.7,
            pos_hint={'top': 1}
        )
        
        # Results display
        self.results = BoxLayout(
            orientation='vertical',
            size_hint_y=0.3
        )
        
        self.scan_button = Button(
            text='Scan',
            size_hint_y=None,
            height=dp(48)
        )
        
        self.add_widget(self.preview)
        self.add_widget(self.overlay)
        self.add_widget(self.results)
        self.add_widget(self.scan_button)
