from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, StringProperty
from kivy.metrics import dp

class CategorySelector(GridLayout):
    categories = ListProperty([
        'Groceries', 'Electronics', 'Clothing',
        'Home', 'Health', 'Other'
    ])
    selected_category = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 3
        self.spacing = dp(8)
        self.padding = dp(8)
        self.size_hint_y = None
        self._setup_categories()
        
    def _setup_categories(self):
        for category in self.categories:
            btn = ToggleButton(
                text=category,
                group='categories',
                size_hint_y=None,
                height=dp(40)
            )
            btn.bind(state=self._on_category_select)
            self.add_widget(btn)
            
    def _on_category_select(self, instance, value):
        if value == 'down':
            self.selected_category = instance.text
            
    def add_category(self, category_name):
        if category_name not in self.categories:
            self.categories.append(category_name)
            self._setup_categories()
