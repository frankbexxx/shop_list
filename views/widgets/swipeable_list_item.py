from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty
from kivy.metrics import dp
from kivy.animation import Animation

class SwipeableListItem(BoxLayout):
    swipe_distance = NumericProperty(0)
    is_swiping = BooleanProperty(False)
    on_delete = ObjectProperty(None)
    on_edit = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(72)
        self._touch_x = 0
        self._setup_layout()
        
    def _setup_layout(self):
        # Main content
        self.content = BoxLayout()
        
        # Action buttons (revealed on swipe)
        self.actions = BoxLayout(
            size_hint_x=None,
            width=dp(120)
        )
        
        self.edit_btn = Button(text='Edit')
        self.delete_btn = Button(text='Delete')
        
        self.actions.add_widget(self.edit_btn)
        self.actions.add_widget(self.delete_btn)
        
        self.add_widget(self.content)
        self.add_widget(self.actions)
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_x = touch.x
            self.is_swiping = True
            return True
        return super().on_touch_down(touch)
        
    def on_touch_move(self, touch):
        if self.is_swiping:
            distance = touch.x - self._touch_x
            self.swipe_distance = max(-120, min(0, distance))
            return True
        return super().on_touch_move(touch)
        
    def on_touch_up(self, touch):
        if self.is_swiping:
            if self.swipe_distance < -60:
                self._complete_swipe()
            else:
                self._reset_swipe()
            self.is_swiping = False
            return True
        return super().on_touch_up(touch)
        
    def _complete_swipe(self):
        Animation(swipe_distance=-120, d=0.2).start(self)
        
    def _reset_swipe(self):
        Animation(swipe_distance=0, d=0.2).start(self)
