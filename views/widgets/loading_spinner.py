from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

class LoadingSpinner(Widget):
    angle = NumericProperty(0)
    size = NumericProperty(dp(48))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self._anim = None
        self._setup_animation()
        
    def _setup_animation(self):
        with self.canvas:
            Color(0.2, 0.6, 0.9, 1)
            self.spinner = Line(
                circle=(self.center_x, self.center_y, self.size/2),
                width=dp(2)
            )
            
    def start(self):
        anim = Animation(angle=360, duration=1)
        anim.bind(on_complete=self._rotate_complete)
        self._anim = anim
        anim.start(self)
        
    def _rotate_complete(self, *args):
        self.angle = 0
        if self._anim:
            self._anim.start(self)
            
    def stop(self):
        if self._anim:
            self._anim.cancel(self)
            self._anim = None
