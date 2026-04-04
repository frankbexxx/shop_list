from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, DictProperty
from kivy.metrics import dp
from kivy.clock import Clock

class SmartSuggestions(GridLayout):
    suggestions = ListProperty([])
    usage_patterns = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.spacing = dp(10)
        self.padding = dp(10)
        self.size_hint_y = None
        self._setup_suggestions()
        
    def _setup_suggestions(self):
        for suggestion in self.suggestions:
            card = SuggestionCard(
                item=suggestion,
                on_select=self._add_to_list
            )
            self.add_widget(card)
            
    def update_suggestions(self, recent_items):
        """Updates suggestions based on shopping patterns"""
        self._analyze_patterns(recent_items)
        self._refresh_display()
        
    def _analyze_patterns(self, items):
        """Analyzes shopping patterns to improve suggestions"""
        for item in items:
            if item.name in self.usage_patterns:
                self.usage_patterns[item.name]['frequency'] += 1
            else:
                self.usage_patterns[item.name] = {'frequency': 1}
