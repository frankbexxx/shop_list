from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ListProperty
from kivy.metrics import dp
from kivy.animation import Animation

class BudgetTracker(BoxLayout):
    budget_limit = NumericProperty(0)
    current_spent = NumericProperty(0)
    spending_history = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(12)
        self.padding = dp(15)
        self._setup_tracker()
        
    def _setup_tracker(self):
        # Budget progress circle
        self.progress_circle = CircularProgress(
            size_hint_y=None,
            height=dp(200)
        )
        
        # Spending breakdown
        self.breakdown = SpendingBreakdown(
            size_hint_y=None,
            height=dp(150)
        )
        
        # Alert threshold slider
        self.alert_slider = AlertSlider(
            size_hint_y=None,
            height=dp(48)
        )
        
        self.add_widget(self.progress_circle)
        self.add_widget(self.breakdown)
        self.add_widget(self.alert_slider)
