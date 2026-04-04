from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty
from kivy.metrics import dp

class ShoppingListTemplate(BoxLayout):
    templates = ListProperty([])
    current_template = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(12)
        self.padding = dp(15)
        self._setup_template_manager()
        
    def _setup_template_manager(self):
        # Template list with preview
        self.template_list = TemplateList(
            size_hint_y=0.6
        )
        
        # Template editor
        self.editor = TemplateEditor(
            size_hint_y=0.4
        )
        
        # Quick actions bar
        self.actions = QuickActions(
            size_hint_y=None,
            height=dp(48)
        )
        
        self.add_widget(self.template_list)
        self.add_widget(self.editor)
        self.add_widget(self.actions)
