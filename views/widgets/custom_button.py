from kivy.uix.button import Button
from kivy.properties import ListProperty, NumericProperty
from kivy.metrics import dp
from kivy.animation import Animation

class CustomButton(Button):
    ripple_color = ListProperty([0.8, 0.8, 0.8, 0.5])
    ripple_duration = NumericProperty(0.3)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = [0.2, 0.6, 0.9, 1]
        self.border_radius = [dp(5)]
        self.min_height = dp(48)
        self._ripple_pos = None
        
    def on_press(self):
        self._ripple_pos = self.pos
        anim = Animation(
            background_color=[0.1, 0.5, 0.8, 1],
            duration=self.ripple_duration
        )
        anim.start(self)
        
    def on_release(self):
        anim = Animation(
            background_color=[0.2, 0.6, 0.9, 1],
            duration=self.ripple_duration
        )
        anim.start(self)

