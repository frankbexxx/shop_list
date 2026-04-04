from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, ListProperty
from kivy.metrics import dp
from kivy.garden.graph import Graph, LinePlot

class PriceHistory(BoxLayout):
    price_data = DictProperty({})
    tracked_items = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(12)
        self._setup_price_tracker()
        
    def _setup_price_tracker(self):
        # Price graph
        self.price_graph = PriceGraph(
            size_hint_y=0.5
        )
        
        # Statistics panel
        self.stats_panel = StatsPanel(
            size_hint_y=0.3
        )
        
        # Price alerts
        self.price_alerts = PriceAlerts(
            size_hint_y=0.2
        )
        
        self.add_widget(self.price_graph)
        self.add_widget(self.stats_panel)
        self.add_widget(self.price_alerts)
