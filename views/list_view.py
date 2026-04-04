from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from views.base_view import BaseView
from views.widgets.custom_button import CustomButton

class ListView(BaseView):
    def __init__(self, shopping_list=None, **kwargs):
        super().__init__(**kwargs)
        self.shopping_list = shopping_list
        self.sort_options = {
            'name': 'Name',
            'category': 'Category',
            'price': 'Price'
        }
        self._setup_layout()
        
    def _setup_layout(self):
        self.layout = BoxLayout(orientation='vertical')
        
        # Controls bar
        self.controls = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8)
        )
        
        self.sort_spinner = Spinner(
            text='Sort by',
            values=list(self.sort_options.values()),
            size_hint_x=0.3
        )
        
        self.add_button = CustomButton(
            text='+',
            size_hint_x=None,
            width=dp(48)
        )
        
        self.controls.add_widget(self.sort_spinner)
        self.controls.add_widget(self.add_button)
        
        # Items list
        self.items_view = RecycleView()
        self.items_view.viewclass = 'ItemView'
        
        self.layout.add_widget(self.controls)
        self.layout.add_widget(self.items_view)
        self.add_widget(self.layout)
        
    def display_items(self):
        if self.shopping_list:
            self.items_view.data = [
                {'item': item} for item in self.shopping_list.items
            ]
            
    def update_sort(self, sort_key):
        if self.shopping_list:
            self.shopping_list.sort_items(key=sort_key)
            self.display_items()
            
    def refresh_view(self):
        self.display_items()
