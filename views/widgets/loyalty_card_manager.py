from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, NumericProperty
from kivy.metrics import dp

class LoyaltyCardManager(BoxLayout):
    cards = DictProperty({})
    total_savings = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self._setup_card_manager()
        
    def _setup_card_manager(self):
        # Digital cards carousel
        self.cards_carousel = CardCarousel(
            size_hint_y=0.4
        )
        
        # Points tracker
        self.points_tracker = PointsTracker(
            size_hint_y=0.3
        )
        
        # Savings summary
        self.savings_summary = SavingsSummary(
            size_hint_y=0.3
        )
        
        # Add card button
        self.add_card = AddCardButton(
            size_hint_y=None,
            height=dp(48),
            text='Add New Card'
        )
        
        self.add_widget(self.cards_carousel)
        self.add_widget(self.points_tracker)
        self.add_widget(self.savings_summary)
        self.add_widget(self.add_card)
