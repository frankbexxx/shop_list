from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ColorProperty, BooleanProperty

class ListHeader(BoxLayout):
    title = StringProperty('')
    subtitle = StringProperty('')
    show_action_button = BooleanProperty(True)
    background_color = ColorProperty([0.95, 0.95, 0.95, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_header()
        
    def _setup_header(self):
        self.orientation = 'horizontal'
        self.padding = ('16dp', '12dp')
        self.spacing = '8dp'
        self.size_hint_y = None
        self.height = '64dp'
