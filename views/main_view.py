from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from views.base_view import BaseView
from views.widgets.custom_button import CustomButton
from views.widgets.search_bar import SearchBar

class MainView(BaseView):
    current_user = ObjectProperty(None)
    screen_manager = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = ScreenManager()
        self._setup_layout()
        self._setup_navigation()
        
    def _setup_layout(self):
        self.main_layout = BoxLayout(orientation='vertical')
        self.toolbar = self._create_toolbar()
        self.main_layout.add_widget(self.toolbar)
        self.main_layout.add_widget(self.screen_manager)
        self.add_widget(self.main_layout)
        
    def _create_toolbar(self):
        toolbar = BoxLayout(
            size_hint_y=None, 
            height=dp(56),
            padding=[dp(8)]
        )
        search = SearchBar()
        menu_button = CustomButton(
            text='Menu',
            size_hint_x=None,
            width=dp(48)
        )
        toolbar.add_widget(menu_button)
        toolbar.add_widget(search)
        return toolbar
        
    def _setup_navigation(self):
        screens = [
            ('lists', 'My Lists'),
            ('items', 'Items'),
            ('settings', 'Settings')
        ]
        for screen_id, title in screens:
            screen = Screen(name=screen_id)
            self.screen_manager.add_widget(screen)
            
    def switch_view(self, screen_name: str):
        self.screen_manager.current = screen_name
        
    def update_navigation(self):
        self._setup_navigation()
        
    def show_settings(self):
        self.switch_view('settings')
