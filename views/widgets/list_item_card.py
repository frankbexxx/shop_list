from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.metrics import dp
from kivy.animation import Animation

class ListItemCard(ButtonBehavior, BoxLayout):
    item = ObjectProperty(None)
    selected = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(8)
        self.spacing = dp(4)
        self.size_hint_y = None
        self.height = dp(120)
        self._setup_layout()
        
    def _setup_layout(self):
        # Header with name and price
        self.header = BoxLayout(size_hint_y=0.4)
        
        # Details section
        self.details = BoxLayout(size_hint_y=0.4)
        
        # Actions section
        self.actions = BoxLayout(size_hint_y=0.2)
        
        self.add_widget(self.header)
        self.add_widget(self.details)
        self.add_widget(self.actions)
        
    def on_item(self, instance, value):
        if value:
            self.update_display()
            
    def update_display(self):
        self._animate_update()
        
    def _animate_update(self):
        anim = Animation(opacity=0, duration=0.1) + Animation(opacity=1, duration=0.2)
        anim.start(self)

