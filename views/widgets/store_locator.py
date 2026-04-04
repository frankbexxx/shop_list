from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, NumericProperty
from kivy.metrics import dp

class StoreLocator(BoxLayout):
    nearby_stores = ListProperty([])
    search_radius = NumericProperty(5.0)  # kilometers
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(12)
        self._setup_locator()
        
    def _setup_locator(self):
        # Map view
        self.map_view = StoreMapView(
            size_hint_y=0.5
        )
        
        # Store list
        self.store_list = NearbyStoreList(
            size_hint_y=0.3
        )
        
        # Filter options
        self.filters = StoreFilters(
            size_hint_y=0.2
        )
        
        # Distance slider
        self.radius_slider = RadiusSlider(
            size_hint_y=None,
            height=dp(48)
        )
        
        self.add_widget(self.map_view)
        self.add_widget(self.store_list)
        self.add_widget(self.filters)
        self.add_widget(self.radius_slider)
