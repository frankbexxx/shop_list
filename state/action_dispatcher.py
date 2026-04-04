from kivy.event import EventDispatcher
from kivy.properties import DictProperty, ListProperty

class ActionDispatcher(EventDispatcher):
    actions = DictProperty({})
    action_history = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_actions()
        
    def _setup_actions(self):
        self.actions = {
            'list': {
                'create': self.create_list,
                'update': self.update_list,
                'delete': self.delete_list
            },
            'item': {
                'add': self.add_item,
                'remove': self.remove_item,
                'modify': self.modify_item
            },
            'category': {
                'create': self.create_category,
                'update': self.update_category,
                'delete': self.delete_category
            }
        }
        
    def dispatch_action(self, action_type, payload):
        category, action = action_type.split('.')
        if category in self.actions and action in self.actions[category]:
            self.action_history.append({'type': action_type, 'payload': payload})
            return self.actions[category][action](payload)
