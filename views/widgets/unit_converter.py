from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, StringProperty
from kivy.metrics import dp

class UnitConverter(BoxLayout):
    conversion_rates = DictProperty({
        'weight': {
            'kg': {'g': 1000, 'oz': 35.274, 'lb': 2.20462},
            'g': {'kg': 0.001, 'oz': 0.035274, 'lb': 0.00220462},
            'oz': {'g': 28.3495, 'kg': 0.0283495, 'lb': 0.0625},
            'lb': {'g': 453.592, 'kg': 0.453592, 'oz': 16}
        },
        'volume': {
            'l': {'ml': 1000, 'fl_oz': 33.814, 'gal': 0.264172},
            'ml': {'l': 0.001, 'fl_oz': 0.033814, 'gal': 0.000264172},
            'fl_oz': {'ml': 29.5735, 'l': 0.0295735, 'gal': 0.0078125},
            'gal': {'ml': 3785.41, 'l': 3.78541, 'fl_oz': 128}
        }
    })
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self._setup_converter()
        
    def _setup_converter(self):
        # Unit selection spinners
        self.unit_selectors = UnitSelectors(
            size_hint_y=0.3
        )
        
        # Conversion input/output
        self.converter_display = ConverterDisplay(
            size_hint_y=0.4
        )
        
        # Quick conversion buttons
        self.quick_convert = QuickConvertButtons(
            size_hint_y=0.3
        )
        
        self.add_widget(self.unit_selectors)
        self.add_widget(self.converter_display)
        self.add_widget(self.quick_convert)
