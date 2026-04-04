from base_controller import BaseController
from kivy.properties import ListProperty, DictProperty

class ListController(BaseController):
    active_lists = ListProperty([])
    list_cache = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_list_controller()
        
    def _setup_list_controller(self):
        self.list_actions = {
            'create_list': self.create_list,
            'update_list': self.update_list,
            'delete_list': self.delete_list,
            'share_list': self.share_list,
            'add_item': self.add_item,
            'remove_item': self.remove_item
        }
        
    def create_list(self, list_data):
        if self.validate_list_data(list_data):
            new_list = self._create_list_object(list_data)
            self.active_lists.append(new_list)
            return new_list
        return None
