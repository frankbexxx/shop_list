from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, BooleanProperty
from kivy.metrics import dp

class MultiSelectList(BoxLayout):
    items = ListProperty([])
    selected_items = ListProperty([])
    selection_mode = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(2)
        self._setup_header()
        self._setup_list()
        
    def _setup_header(self):
        self.header = BoxLayout(
            size_hint_y=None,
            height=dp(48)
        )
        
        self.select_all = CheckBox(
            size_hint_x=0.1,
            active=False
        )
        self.select_all.bind(active=self._toggle_all)
        
        self.action_bar = BoxLayout(size_hint_x=0.9)
        
        self.header.add_widget(self.select_all)
        self.header.add_widget(self.action_bar)
        self.add_widget(self.header)
        
    def _setup_list(self):
        self.list_container = BoxLayout(orientation='vertical')
        for item in self.items:
            self._add_item_widget(item)
        self.add_widget(self.list_container)
        
    def _add_item_widget(self, item):
        item_row = SelectableItem(
            item=item,
            on_select=self._on_item_select
        )
        self.list_container.add_widget(item_row)
        
    def _toggle_all(self, instance, value):
        if value:
            self.selected_items = self.items.copy()
        else:
            self.selected_items.clear()
