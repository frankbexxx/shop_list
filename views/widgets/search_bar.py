from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.properties import ListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.metrics import dp

class SearchBar(BoxLayout):
    suggestions = ListProperty([])
    on_search = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.height = dp(48)
        self.size_hint_y = None
        self.padding = [dp(8)]
        
        # Search input
        self.search_input = TextInput(
            multiline=False,
            hint_text='Search...',
            size_hint_x=0.9,
            padding=[dp(12), dp(12), 0, 0]
        )
        self.search_input.bind(text=self._on_text_change)
        
        # Clear button
        self.clear_button = Button(
            text='×',
            size_hint_x=0.1,
            background_normal='',
            background_color=[0.9, 0.9, 0.9, 1]
        )
        self.clear_button.bind(on_release=self.clear_search)
        
        self.add_widget(self.search_input)
        self.add_widget(self.clear_button)
        
    def _on_text_change(self, instance, value):
        Clock.unschedule(self._trigger_search)
        Clock.schedule_once(self._trigger_search, 0.5)
        
    def _trigger_search(self, dt):
        if self.on_search:
            self.on_search(self.search_input.text)
            
    def clear_search(self, *args):
        self.search_input.text = ''
        
    def update_suggestions(self, suggestions):
        self.suggestions = suggestions
