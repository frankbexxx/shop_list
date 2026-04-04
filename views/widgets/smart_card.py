from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ListProperty
from kivy.metrics import dp
from kivy.clock import Clock

class SmartCart(BoxLayout):
    current_total = NumericProperty(0)
    cart_items = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self._setup_cart()
        
    def _setup_cart(self):
        # Running total display
        self.total_display = TotalDisplay(
            size_hint_y=0.2
        )
        
        # Live cart contents
        self.cart_view = CartView(
            size_hint_y=0.5
        )
        
        # Budget progress
        self.budget_tracker = BudgetProgress(
            size_hint_y=0.2
        )
        
        # Quick checkout button
        self.checkout_button = CheckoutButton(
            size_hint_y=0.1
        )
        
        self.add_widget(self.total_display)
        self.add_widget(self.cart_view)
        self.add_widget(self.budget_tracker)
        self.add_widget(self.checkout_button)
