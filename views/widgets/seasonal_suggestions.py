from kivy.uix.scrollview import ScrollView
from kivy.properties import DictProperty, StringProperty
from kivy.metrics import dp

class SeasonalSuggestions(ScrollView):
    current_season = StringProperty('')
    seasonal_items = DictProperty({
        'summer': ['sunscreen', 'ice cream', 'water'],
        'winter': ['hot chocolate', 'soup', 'tea'],
        'spring': ['allergy medicine', 'umbrella'],
        'fall': ['pumpkin spice', 'apple cider']
    })
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(200)
        self._setup_suggestions()
        
    def _setup_suggestions(self):
        # Main container
        self.container = GridLayout(
            cols=2,
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        
        # Season selector
        self.season_tabs = SeasonTabs(
            size_hint_y=None,
            height=dp(40)
        )
        
        # Suggestions grid
        self.suggestions_grid = SuggestionsGrid()
        
        self.container.add_widget(self.season_tabs)
        self.container.add_widget(self.suggestions_grid)
        self.add_widget(self.container)
