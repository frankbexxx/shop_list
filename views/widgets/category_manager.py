from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, DictProperty
from kivy.metrics import dp

class CategoryManager(BoxLayout):
    categories = ListProperty([])
    category_icons = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self._setup_manager()
        
    def _setup_manager(self):
        # Category grid
        self.category_grid = CategoryGrid(
            size_hint_y=0.5
        )
        
        # Icon selector
        self.icon_selector = IconSelector(
            size_hint_y=0.2
        )
        
        # Category editor
        self.category_editor = CategoryEditor(
            size_hint_y=0.3
        )
        
        # Add category button
        self.add_button = AddCategoryButton(
            size_hint_y=None,
            height=dp(48)
        )
        
        self.add_widget(self.category_grid)
        self.add_widget(self.icon_selector)
        self.add_widget(self.category_editor)
        self.add_widget(self.add_button)
