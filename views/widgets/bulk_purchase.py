from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, DictProperty
from kivy.metrics import dp

class BulkPurchase(BoxLayout):
    bulk_discounts = DictProperty({})
    minimum_quantities = DictProperty({})
    total_savings = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(12)
        self._setup_bulk_calculator()
        
    def _setup_bulk_calculator(self):
        # Quantity selector
        self.quantity_selector = QuantitySelector(
            size_hint_y=0.3
        )
        
        # Discount tiers display
        self.discount_tiers = DiscountTiers(
            size_hint_y=0.3
        )
        
        # Savings calculator
        self.savings_display = SavingsDisplay(
            size_hint_y=0.3
        )
        
        # Order button
        self.order_button = OrderButton(
            size_hint_y=0.1
        )
        
        self.add_widget(self.quantity_selector)
        self.add_widget(self.discount_tiers)
        self.add_widget(self.savings_display)
        self.add_widget(self.order_button)
