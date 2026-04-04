from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, ListProperty
from kivy.metrics import dp
from kivy.garden.graph import Graph, MeshLinePlot

class ShoppingListStats(BoxLayout):
    spending_data = DictProperty({})
    categories = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(16)
        self.spacing = dp(16)
        self._setup_charts()
        
    def _setup_charts(self):
        # Spending over time graph
        self.spending_graph = Graph(
            xlabel='Time',
            ylabel='Amount',
            x_ticks_minor=5,
            x_ticks_major=25,
            y_ticks_major=10,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=-0,
            xmax=100,
            ymin=-0,
            ymax=100
        )
        
        # Category distribution pie chart
        self.category_chart = PieChart(
            size_hint_y=None,
            height=dp(200)
        )
        
        self.add_widget(self.spending_graph)
        self.add_widget(self.category_chart)
