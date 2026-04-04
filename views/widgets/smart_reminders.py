from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.metrics import dp

class SmartReminders(BoxLayout):
    reminders = ListProperty([])
    notifications_enabled = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self._setup_reminders()
        
    def _setup_reminders(self):
        # Reminder cards container
        self.reminder_list = ReminderList()
        
        # Quick add reminder
        self.quick_add = QuickAddReminder(
            size_hint_y=None,
            height=dp(48)
        )
        
        # Settings panel
        self.settings = ReminderSettings(
            size_hint_y=None,
            height=dp(120)
        )
        
        self.add_widget(self.reminder_list)
        self.add_widget(self.quick_add)
        self.add_widget(self.settings)
