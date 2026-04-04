from kivy.uix.widget import Widget
from kivy.properties import ListProperty, NumericProperty
from kivy.animation import Animation
from kivy.metrics import dp
from math import cos, sin, pi

class BlastMenu(Widget):
    items = ListProperty([])
    radius = NumericProperty(dp(100))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.buttons = []
        self.is_open = False
        self._setup_menu()
        
    def _setup_menu(self):
        # Main trigger button
        self.trigger = BlastButton(
            text='+',
            size=(dp(56), dp(56)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.trigger.bind(on_release=self.toggle)
        self.add_widget(self.trigger)
        
        # Create action buttons
        for idx, item in enumerate(self.items):
            btn = BlastButton(
                text=item['icon'],
                size=(dp(48), dp(48)),
                opacity=0
            )
            btn.bind(on_release=lambda x, i=item: self._handle_action(i))
            self.buttons.append(btn)
            self.add_widget(btn)
            
    def toggle(self, *args):
        if self.is_open:
            self._close_menu()
        else:
            self._open_menu()
            
    def _open_menu(self):
        self.is_open = True
        for idx, btn in enumerate(self.buttons):
            angle = 2 * pi * idx / len(self.buttons)
            x = self.radius * cos(angle)
            y = self.radius * sin(angle)
            
            anim = Animation(
                pos_hint={'center_x': 0.5 + x/self.width,
                         'center_y': 0.5 + y/self.height},
                opacity=1,
                duration=0.3,
                t='out_elastic'
            )
            anim.start(btn)
            
    def _close_menu(self):
        self.is_open = False
        for btn in self.buttons:
            anim = Animation(
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                opacity=0,
                duration=0.2
            )
            anim.start(btn)
