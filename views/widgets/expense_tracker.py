from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, NumericProperty
from kivy.metrics import dp

class ExpenseTracker(BoxLayout):
    expenses = DictProperty({})
    monthly_budget = NumericProperty(0)
    total_spent = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self._setup_expense_tracker()
        
    def _setup_expense_tracker(self):
        # Expense summary
        self.summary = ExpenseSummary(
            size_hint_y=0.3
        )
        
        # Category breakdown
        self.category_breakdown = CategoryBreakdown(
            size_hint_y=0.3
        )
        
        # Trend analysis
        self.trend_analysis = TrendAnalysis(
            size_hint_y=0.3
        )
        
        # Export report button
        self.export_button = ExportButton(
            size_hint_y=0.1
        )
        
        self.add_widget(self.summary)
        self.add_widget(self.category_breakdown)
        self.add_widget(self.trend_analysis)
        self.add_widget(self.export_button)
