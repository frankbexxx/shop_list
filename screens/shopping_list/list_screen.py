from common.base_screen import BaseScreen
from kivy.properties import ObjectProperty, StringProperty

class ListScreen(BaseScreen):
    view = ObjectProperty(None)
    list_id = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_list_screen()
        
    def _setup_list_screen(self):
        self.screen_title = 'Shopping List'
        
    def load_list(self, list_id):
        self.list_id = list_id
        self.controller.load_list_data(list_id)
