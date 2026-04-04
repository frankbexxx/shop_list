from kivy.event import EventDispatcher
from kivy.properties import ListProperty, DictProperty

class NotificationService(EventDispatcher):
    notifications = ListProperty([])
    channels = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_notification_service()
        
    def _setup_notification_service(self):
        self.notification_types = {
            'push': self._send_push,
            'in_app': self._send_in_app,
            'email': self._send_email,
            'reminder': self._send_reminder
        }
        
    def send_notification(self, notification_type, data):
        if notification_type in self.notification_types:
            return self.notification_types[notification_type](data)
