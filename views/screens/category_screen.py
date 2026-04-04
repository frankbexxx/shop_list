from kivy.uix.screenmanager import Screen
from kivy.properties import DictProperty
from kivy.metrics import dp

class CategoryScreen(Screen):
    category_data = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main container
        self.layout = BoxLayout(orientation='vertical')
        
        # Category manager
        self.category_manager = CategoryManager()
        
        # Category stats
        self.stats_view = CategoryStats()
        
        # Smart labels
        self.smart_labels = SmartLabels()
        
        # Quick filters
        self.filters = QuickFilters()
        
        # Add components
        self.layout.add_widget(self.category_manager)
        self.layout.add_widget(self.stats_view)
        self.layout.add_widget(self.smart_labels)
        self.layout.add_widget(self.filters)
        
        self.add_widget(self.layout)
