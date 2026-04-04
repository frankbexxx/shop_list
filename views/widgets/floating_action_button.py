from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ListProperty
from kivy.metrics import dp
from kivy.animation import Animation

class FloatingActionButton(ButtonBehavior, FloatLayout):
    icon = StringProperty('+')
    background_color = ListProperty([0.2, 0.6, 0.9, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(56), dp(56))
        self.pos_hint = {'right': 0.95, 'bottom': 0.1}
        self._setup_layout()
        
    def _setup_layout(self):
        with self.canvas.before:
            Color(*self.background_color)
            self.circle = Ellipse(
                pos=self.pos,
                size=self.size
            )
            
        self.label = Label(
            text=self.icon,
            pos=self.pos,
            size=self.size,
            font_size=dp(24)
        )
        self.add_widget(self.label)
        
    def on_press(self):
        anim = Animation(
            background_color=[0.1, 0.5, 0.8, 1],
            duration=0.1
        )
        anim.start(self)
        
    def on_release(self):
        anim = Animation(
            background_color=self.background_color,
            duration=0.1
        )
        anim.start(self)
