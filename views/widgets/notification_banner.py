from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.clock import Clock

class NotificationBanner(BoxLayout):
    message = StringProperty('')
    duration = NumericProperty(3)  # seconds
    type = StringProperty('info')  # info, success, error, warning
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.opacity = 0
        self._setup_layout()
        
    def _setup_layout(self):
        self.icon = Label(
            size_hint_x=0.1,
            font_name='MaterialIcons'
        )
        
        self.message_label = Label(
            text=self.message,
            size_hint_x=0.8
        )
        
        self.close_btn = Button(
            text='×',
            size_hint_x=0.1,
            on_release=self.dismiss
        )
        
        self.add_widget(self.icon)
        self.add_widget(self.message_label)
        self.add_widget(self.close_btn)
        
    def show(self, message, type='info'):
        self.message = message
        self.type = type
        self._update_style()
        self._animate_in()
        Clock.schedule_once(self.dismiss, self.duration)
        
    def _animate_in(self):
        Animation(opacity=1, duration=0.3).start(self)
        
    def dismiss(self, *args):
        anim = Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=lambda *x: self.parent.remove_widget(self))
        anim.start(self)
