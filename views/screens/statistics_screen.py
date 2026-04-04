from kivy.uix.screenmanager import Screen
from kivy.properties import DictProperty, ListProperty
from kivy.metrics import dp

class StatisticsScreen(Screen):
    shopping_stats = DictProperty({})
    trends = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main container
        self.layout = BoxLayout(orientation='vertical')
        
        # Spending overview
        self.spending_overview = SpendingOverview()
        
        # Shopping patterns
        self.patterns = ShoppingPatterns()
        
        # Category analysis
        self.category_analysis = CategoryAnalysis()
        
        # Export tools
        self.export_tools = ExportTools()
        
        # Add components
        self.layout.add_widget(self.spending_overview)
        self.layout.add_widget(self.patterns)
        self.layout.add_widget(self.category_analysis)
        self.layout.add_widget(self.export_tools)
        
        self.add_widget(self.layout)
