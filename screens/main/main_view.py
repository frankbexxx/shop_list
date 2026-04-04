from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, ListProperty
from ui.components.buttons.primary_button import PrimaryButton

class MainView(BoxLayout):
    controller = ObjectProperty(None)
    lists = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_view()
        
    def _setup_view(self):
        self.orientation = 'vertical'
        self.spacing = '16dp'
        self.padding = '16dp'
        
        self.add_button = PrimaryButton(
            text='Create New List',
            on_press=self.controller.create_new_list
        )
