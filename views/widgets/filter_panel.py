from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, ListProperty
from kivy.metrics import dp

class FilterPanel(BoxLayout):
    filters = DictProperty({
        'price_range': (0, 1000),
        'categories': [],
        'sort_by': 'name',
        'sort_order': 'asc'
    })
    
    active_filters = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(8)
        self._setup_filters()
        
    def _setup_filters(self):
        # Price Range Slider
        self.price_slider = RangeSlider(
            range=(0, 1000),
            value=self.filters['price_range']
        )
        
        # Categories MultiSelect
        self.category_select = ChipSelect(
            choices=self.filters['categories']
        )
        
        # Sort Options
        self.sort_spinner = Spinner(
            text='Sort by',
            values=['name', 'price', 'date']
        )
        
        # Order Toggle
        self.order_toggle = ToggleButton(
            text='↑↓'
        )
        
        self._add_filter_widgets()
        
    def _add_filter_widgets(self):
        self.add_widget(Label(text='Price Range'))
        self.add_widget(self.price_slider)
        self.add_widget(Label(text='Categories'))
        self.add_widget(self.category_select)
        self.add_widget(self.sort_spinner)
        self.add_widget(self.order_toggle)
