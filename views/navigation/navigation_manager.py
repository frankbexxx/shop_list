from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.properties import ObjectProperty
from kivy.event import EventDispatcher

class NavigationManager(ScreenManager, EventDispatcher):
    current_route = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()
        self._setup_routes()
        self._bind_events()
        
    def _setup_routes(self):
        self.routes = {
            'main': MainScreen,
            'shopping_list': ShoppingListScreen,
            'category': CategoryScreen,
            'budget': BudgetScreen,
            'family': FamilyScreen,
            'store': StoreScreen,
            'meal_planner': MealPlannerScreen,
            'settings': SettingsScreen,
            'profile': ProfileScreen,
            'statistics': StatisticsScreen,
            'notifications': NotificationsScreen,
            'import_export': ImportExportScreen,
            'smart_cart': SmartCartScreen
        }
        
    def navigate_to(self, route_name, **params):
        if route_name in self.routes:
            self.current = route_name
            self.current_route = route_name
            self._handle_params(params)
