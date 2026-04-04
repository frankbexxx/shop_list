from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.metrics import dp
from kivy.uix.label import Label

class StatusBar(BoxLayout):
    total_items = NumericProperty(0)
    total_cost = NumericProperty(0.0)
    status = StringProperty('Active')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)
        self.padding = [dp(8)]
        self.spacing = dp(10)
        
        self._setup_layout()
        
    def _setup_layout(self):
        # Items counter
        self.items_label = Label(size_hint_x=0.3)
        
        # Total cost
        self.cost_label = Label(size_hint_x=0.4)
        
        # Status indicator
        self.status_label = Label(size_hint_x=0.3)
        
        self.add_widget(self.items_label)
        self.add_widget(self.cost_label)
        self.add_widget(self.status_label)
        
    def update_display(self):
        self.items_label.text = f'Items: {self.total_items}'
        self.cost_label.text = f'Total: ${self.total_cost:.2f}'
        self.status_label.text = f'Status: {self.status}'
