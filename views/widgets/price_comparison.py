from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, ListProperty
from kivy.metrics import dp

class PriceComparison(BoxLayout):
    stores = ListProperty([])
    price_data = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self._setup_comparison_view()
        
    def _setup_comparison_view(self):
        # Store selector
        self.store_tabs = TabBar(
            size_hint_y=None,
            height=dp(48)
        )
        
        # Price grid
        self.price_grid = GridLayout(
            cols=3,  # Store, Price, Date
            spacing=dp(5)
        )
        
        # Best price indicator
        self.best_price = BestPriceCard(
            size_hint_y=None,
            height=dp(80)
        )
        
        self.add_widget(self.store_tabs)
        self.add_widget(self.price_grid)
        self.add_widget(self.best_price)
