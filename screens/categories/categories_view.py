from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, ListProperty
from ui.components.buttons.primary_button import PrimaryButton

class CategoriesView(BoxLayout):
    controller = ObjectProperty(None)
    categories = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_view()
        
    def _setup_view(self):
        self.orientation = 'vertical'
        self.spacing = '16dp'
        
        self.add_button = PrimaryButton(
            text='Add Category',
            on_press=self.controller.create_category
        )
