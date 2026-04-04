from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.metrics import dp
from views.base_view import BaseView
from views.widgets.custom_button import CustomButton

class ItemView(BaseView):
    item = ObjectProperty(None)
    selected = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = dp(72)
        self.size_hint_y = None
        self._setup_layout()
        
    def _setup_layout(self):
        self.layout = BoxLayout(padding=dp(8), spacing=dp(8))
        
        # Main content
        self.content = BoxLayout(orientation='vertical')
        self.name_price = BoxLayout()
        self.details = BoxLayout()
        
        # Action buttons
        self.actions = BoxLayout(
            size_hint_x=0.3,
            spacing=dp(4)
        )
        
        self.edit_btn = CustomButton(
            text='Edit',
            size_hint_x=None,
            width=dp(48)
        )
        
        self.check_btn = CustomButton(
            text='✓',
            size_hint_x=None,
            width=dp(48)
        )
        
        self.actions.add_widget(self.edit_btn)
        self.actions.add_widget(self.check_btn)
        
        self.layout.add_widget(self.content)
        self.layout.add_widget(self.actions)
        self.add_widget(self.layout)
        
    def on_item(self, instance, value):
        if value:
            self.update_display()
            
    def update_display(self):
        self.name_price.clear_widgets()
        self.details.clear_widgets()
        
        # Update item information display
        if self.item:
            self.name_price.add_widget(
                Label(
                    text=self.item.name,
                    bold=True,
                    size_hint_x=0.7
                )
            )
            self.name_price.add_widget(
                Label(
                    text=f"${self.item.price}",
                    size_hint_x=0.3
                )
            )
            
            self.details.add_widget(
                Label(
                    text=f"{self.item.quantity} {self.item.unit}",
                    size_hint_x=0.5
                )
            )
            self.details.add_widget(
                Label(
                    text=self.item.category,
                    size_hint_x=0.5
                )
            )
            
    def on_selected(self, instance, value):
        self.canvas.color = self.theme['primary'] if value else self.theme['background']
