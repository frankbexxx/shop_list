from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, NumericProperty
from kivy.metrics import dp
from kivy.clock import Clock

class ShoppingModeView(BoxLayout):
    items = ListProperty([])
    total_spent = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(15)
        self._setup_layout()
        
    def _setup_layout(self):
        # Progress bar
        self.progress = ProgressBar(
            size_hint_y=None,
            height=dp(20)
        )
        
        # Items remaining counter
        self.counter = Label(
            size_hint_y=None,
            height=dp(30)
        )
        
        # Main shopping list
        self.list_view = ShoppingList()
        
        # Total spent display
        self.total_display = TotalDisplay()
        
        # Add all components
        self.add_widget(self.progress)
        self.add_widget(self.counter)
        self.add_widget(self.list_view)
        self.add_widget(self.total_display)
