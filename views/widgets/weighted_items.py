from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, DictProperty
from kivy.metrics import dp

class WeightedItems(BoxLayout):
    price_per_unit = NumericProperty(0)
    total_weight = NumericProperty(0)
    weight_units = DictProperty({
        'kg': 1.0,
        'g': 0.001,
        'lb': 0.453592,
        'oz': 0.0283495
    })
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self._setup_weight_calculator()
        
    def _setup_weight_calculator(self):
        # Weight input
        self.weight_input = WeightInput(
            size_hint_y=0.3
        )
        
        # Unit price calculator
        self.price_calculator = PriceCalculator(
            size_hint_y=0.3
        )
        
        # Comparison tool
        self.comparison_tool = UnitPriceComparison(
            size_hint_y=0.3
        )
        
        # Quick calculate button
        self.calculate_button = CalculateButton(
            size_hint_y=0.1
        )
        
        self.add_widget(self.weight_input)
        self.add_widget(self.price_calculator)
        self.add_widget(self.comparison_tool)
        self.add_widget(self.calculate_button)
