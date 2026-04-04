from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, DictProperty
from kivy.metrics import dp

class StoreScreen(Screen):
    nearby_stores = ListProperty([])
    price_data = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main container
        self.layout = BoxLayout(orientation='vertical')
        
        # Store locator
        self.store_locator = StoreLocator()
        
        # Price comparison
        self.price_comparison = PriceComparison()
        
        # Loyalty cards
        self.loyalty_manager = LoyaltyCardManager()
        
        # Store preferences
        self.store_preferences = StorePreferences()
        
        # Add components
        self.layout.add_widget(self.store_locator)
        self.layout.add_widget(self.price_comparison)
        self.layout.add_widget(self.loyalty_manager)
        self.layout.add_widget(self.store_preferences)
        
        self.add_widget(self.layout)
