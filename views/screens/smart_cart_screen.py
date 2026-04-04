from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, NumericProperty
from kivy.metrics import dp

class SmartCartScreen(Screen):
    cart_items = ListProperty([])
    total_amount = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main container
        self.layout = BoxLayout(orientation='vertical')
        
        # Smart cart view
        self.smart_cart = SmartCart()
        
        # Barcode scanner
        self.barcode_scanner = BarcodeScanner()
        
        # Price checker
        self.price_checker = PriceChecker()
        
        # Checkout panel
        self.checkout_panel = CheckoutPanel()
        
        # Add components
        self.layout.add_widget(self.smart_cart)
        self.layout.add_widget(self.barcode_scanner)
        self.layout.add_widget(self.price_checker)
        self.layout.add_widget(self.checkout_panel)
        
        self.add_widget(self.layout)
