from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty
from kivy.metrics import dp

class ImportExport(BoxLayout):
    supported_formats = ListProperty(['CSV', 'JSON', 'PDF'])
    export_path = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self._setup_tools()
        
    def _setup_tools(self):
        # Format selector
        self.format_selector = FormatSelector(
            size_hint_y=0.3
        )
        
        # File browser
        self.file_browser = FileBrowser(
            size_hint_y=0.4
        )
        
        # Options panel
        self.options_panel = ExportOptions(
            size_hint_y=0.2
        )
        
        # Action buttons
        self.action_buttons = ActionButtons(
            size_hint_y=0.1
        )
        
        self.add_widget(self.format_selector)
        self.add_widget(self.file_browser)
        self.add_widget(self.options_panel)
        self.add_widget(self.action_buttons)
