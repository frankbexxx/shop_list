from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, ObjectProperty
from kivy.metrics import dp
from kivy.animation import Animation

class QuickActionBar(BoxLayout):
    actions = ListProperty([])
    on_action = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(56)
        self.padding = [dp(8)]
        self.spacing = dp(8)
        self._setup_actions()
        
    def _setup_actions(self):
        for action in self.actions:
            btn = IconButton(
                icon=action['icon'],
                text=action['label'],
                on_release=lambda x, a=action: self._trigger_action(a)
            )
            self.add_widget(btn)
            
    def _trigger_action(self, action):
        if self.on_action:
            self.on_action(action['id'])
            self._animate_button(action['id'])
            
    def _animate_button(self, action_id):
        for child in self.children:
            if child.action_id == action_id:
                anim = Animation(scale=0.8, duration=0.1) + Animation(scale=1, duration=0.1)
                anim.start(child)
