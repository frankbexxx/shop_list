from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ColorProperty, ObjectProperty
from .text_input import CustomTextInput

class SearchInput(BoxLayout):
    search_text = StringProperty('')
    icon_color = ColorProperty([0.5, 0.5, 0.5, 1])
    on_search = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_search()
        
    def _setup_search(self):
        self.orientation = 'horizontal'
        self.padding = ('8dp', '0dp')
        self.spacing = '8dp'
        
        self.search_field = CustomTextInput(
            hint_text='Search...',
            on_text_validate=self._handle_search
        )
