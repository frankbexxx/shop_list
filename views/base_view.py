from kivy.uix.widget import Widget
from kivy.properties import DictProperty, NumericProperty
from kivy.metrics import dp
from app.config import COLORS, WINDOW_CONFIG

class BaseView(Widget):
    theme = DictProperty(COLORS)
    padding = NumericProperty(dp(8))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.minimum_height = WINDOW_CONFIG['minimum_height']
        self.minimum_width = WINDOW_CONFIG['minimum_width']
        
    def update_view(self):
        """Updates the view's content"""
        self.clear_widgets()
        self._setup_layout()
        
    def _setup_layout(self):
        """Sets up the basic layout structure"""
        pass
        
    def apply_theme(self, theme_dict: dict):
        """Updates the view's theme colors"""
        self.theme.update(theme_dict)
        
    def on_size(self, *args):
        """Handles resize events"""
        self.update_view()
        
    def on_pos(self, *args):
        """Handles position changes"""
        self.update_view()

