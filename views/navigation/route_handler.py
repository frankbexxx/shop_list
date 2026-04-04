from kivy.event import EventDispatcher
from kivy.properties import DictProperty, StringProperty

class RouteHandler(EventDispatcher):
    route_history = DictProperty({})
    current_route = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_routes()
        
    def _setup_routes(self):
        self.routes = {
            'main': {
                'title': 'Home',
                'requires_auth': False
            },
            'shopping_list': {
                'title': 'Shopping Lists',
                'requires_auth': True
            },
            'profile': {
                'title': 'Profile',
                'requires_auth': True
            }
        }
        
    def navigate(self, route_name, params=None):
        if route_name in self.routes:
            self.current_route = route_name
            self.route_history[len(self.route_history)] = {
                'route': route_name,
                'params': params
            }
            return True
        return False
        
    def go_back(self):
        if len(self.route_history) > 1:
            self.route_history.pop(len(self.route_history) - 1)
            last_route = self.route_history[len(self.route_history) - 1]
            self.current_route = last_route['route']
            return True
        return False
