from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, DictProperty
from kivy.metrics import dp

class RecipeIntegration(BoxLayout):
    recipes = ListProperty([])
    ingredients_mapping = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self._setup_recipe_view()
        
    def _setup_recipe_view(self):
        # Recipe browser
        self.recipe_browser = RecipeBrowser(
            size_hint_y=0.6
        )
        
        # Ingredients converter
        self.converter = IngredientsConverter(
            size_hint_y=0.2
        )
        
        # Quick add to list
        self.quick_add = QuickAddPanel(
            size_hint_y=0.2
        )
        
        self.add_widget(self.recipe_browser)
        self.add_widget(self.converter)
        self.add_widget(self.quick_add)
