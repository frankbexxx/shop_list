from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, DictProperty
from kivy.metrics import dp

class MealPlannerScreen(Screen):
    recipes = ListProperty([])
    meal_plan = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_layout()
        
    def _setup_layout(self):
        # Main container
        self.layout = BoxLayout(orientation='vertical')
        
        # Meal planner calendar
        self.meal_planner = MealPlanner()
        
        # Recipe integration
        self.recipe_manager = RecipeIntegration()
        
        # Shopping list generator
        self.list_generator = ShoppingListGenerator()
        
        # Nutritional insights
        self.nutrition_view = NutritionalInsights()
        
        # Add components
        self.layout.add_widget(self.meal_planner)
        self.layout.add_widget(self.recipe_manager)
        self.layout.add_widget(self.list_generator)
        self.layout.add_widget(self.nutrition_view)
        
        self.add_widget(self.layout)
