from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, DictProperty
from kivy.metrics import dp

class SmartLabels(BoxLayout):
    labels = ListProperty([])
    label_colors = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self._setup_label_manager()
        
    def _setup_label_manager(self):
        # Label creator
        self.label_creator = LabelCreator(
            size_hint_y=0.3
        )
        
        # Label cloud
        self.label_cloud = LabelCloud(
            size_hint_y=0.4
        )
        
        # Quick filters
        self.quick_filters = QuickFilters(
            size_hint_y=0.3
        )
        
        self.add_widget(self.label_creator)
        self.add_widget(self.label_cloud)
        self.add_widget(self.quick_filters)
