from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, NumericProperty
from kivy.metrics import dp
from kivy.clock import Clock

class SmartPantry(BoxLayout):
    inventory = DictProperty({})
    restock_threshold = NumericProperty(20)  # percentage
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self._setup_pantry_tracker()
        
    def _setup_pantry_tracker(self):
        # Inventory grid
        self.inventory_grid = InventoryGrid(
            size_hint_y=0.5
        )
        
        # Low stock alerts
        self.alerts = LowStockAlerts(
            size_hint_y=0.2
        )
        
        # Quick restock button
        self.restock_button = QuickRestockButton(
            size_hint_y=None,
            height=dp(48)
        )
        
        # Usage statistics
        self.usage_stats = UsageStatistics(
            size_hint_y=0.3
        )
        
        self.add_widget(self.inventory_grid)
        self.add_widget(self.alerts)
        self.add_widget(self.usage_stats)
        self.add_widget(self.restock_button)
