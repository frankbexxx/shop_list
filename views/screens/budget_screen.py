from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, DictProperty
from kivy.metrics import dp

class BudgetScreen(Screen):
    total_budget = NumericProperty(0)
    expenses = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main container
        self.layout = BoxLayout(orientation='vertical')
        
        # Budget overview
        self.budget_overview = BudgetOverview()
        
        # Expense tracker
        self.expense_tracker = ExpenseTracker()
        
        # Price history
        self.price_history = PriceHistory()
        
        # Savings suggestions
        self.savings = SavingsSuggestions()
        
        # Add components
        self.layout.add_widget(self.budget_overview)
        self.layout.add_widget(self.expense_tracker)
        self.layout.add_widget(self.price_history)
        self.layout.add_widget(self.savings)
        
        self.add_widget(self.layout)
