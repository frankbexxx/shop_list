from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty

class DropdownMenu(Button):
    items = ListProperty([])
    selected = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown = DropDown()
        self.bind(items=self._update_items)
        self.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=self._on_select)
        self.size_hint_y = None
        self.height = dp(48)
        
    def _update_items(self, instance, value):
        self.dropdown.clear_widgets()
        for item in self.items:
            btn = Button(
                text=str(item),
                size_hint_y=None,
                height=dp(48)
            )
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
            
    def _on_select(self, instance, value):
        self.selected = value
        self.text = value
