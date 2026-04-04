from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, DictProperty
from kivy.metrics import dp

class ShoppingHistory(BoxLayout):
    history_entries = ListProperty([])
    spending_trends = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(12)
        self._setup_history_view()
        
    def _setup_history_view(self):
        # Timeline view
        self.timeline = HistoryTimeline(
            size_hint_y=0.4
        )
        
        # Statistics panel
        self.stats_panel = HistoryStats(
            size_hint_y=0.3
        )
        
        # Search and filters
        self.search_filters = HistoryFilters(
            size_hint_y=0.2
        )
        
        # Export options
        self.export_options = ExportTools(
            size_hint_y=0.1
        )
        
        self.add_widget(self.timeline)
        self.add_widget(self.stats_panel)
        self.add_widget(self.search_filters)
        self.add_widget(self.export_options)
