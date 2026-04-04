from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty
from kivy.metrics import dp

class ImportExportScreen(Screen):
    supported_formats = ListProperty(['CSV', 'JSON', 'PDF'])
    current_format = StringProperty('CSV')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main container
        self.layout = BoxLayout(orientation='vertical')
        
        # Format selector
        self.format_selector = FormatSelector()
        
        # Data preview
        self.data_preview = DataPreview()
        
        # Import/Export options
        self.transfer_options = TransferOptions()
        
        # Progress tracker
        self.progress_tracker = ProgressTracker()
        
        # Add components
        self.layout.add_widget(self.format_selector)
        self.layout.add_widget(self.data_preview)
        self.layout.add_widget(self.transfer_options)
        self.layout.add_widget(self.progress_tracker)
        
        self.add_widget(self.layout)
