from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, ListProperty
from kivy.metrics import dp

class MealPlanner(BoxLayout):
    weekly_plan = DictProperty({})
    meal_categories = ListProperty(['Breakfast', 'Lunch', 'Dinner', 'Snacks'])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self._setup_planner()
        
    def _setup_planner(self):
        # Calendar view
        self.calendar = WeeklyCalendar(
            size_hint_y=0.4
        )
        
        # Meal slots
        self.meal_grid = MealGrid(
            size_hint_y=0.4
        )
        
        # Shopping list generator
        self.list_generator = ShoppingListGenerator(
            size_hint_y=0.2
        )
        
        # Quick actions
        self.actions = QuickActionBar(
            size_hint_y=None,
            height=dp(48)
        )
        
        self.add_widget(self.calendar)
        self.add_widget(self.meal_grid)
        self.add_widget(self.list_generator)
        self.add_widget(self.actions)
