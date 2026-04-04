from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.metrics import dp

class DiscountCalculator(BoxLayout):
    original_price = NumericProperty(0)
    discount_percentage = NumericProperty(0)
    final_price = NumericProperty(0)
    savings = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(12)
        self._setup_calculator()
        
    def _setup_calculator(self):
        # Price input
        self.price_input = PriceInput(
            size_hint_y=0.25
        )
        
        # Discount selector
        self.discount_selector = DiscountSelector(
            size_hint_y=0.25
        )
        
        # Results display
        self.results = ResultsDisplay(
            size_hint_y=0.3
        )
        
        # Quick discount buttons
        self.quick_discounts = QuickDiscountButtons(
            size_hint_y=0.2
        )
        
        self.add_widget(self.price_input)
        self.add_widget(self.discount_selector)
        self.add_widget(self.results)
        self.add_widget(self.quick_discounts)
