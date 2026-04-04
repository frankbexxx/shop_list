from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty
from functools import partial

class WidgetMessenger(EventDispatcher):
    event_bus = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_channels()
        
    def _setup_channels(self):
        self.channels = {
            'shopping_list': [],
            'budget': [],
            'family': [],
            'settings': []
        }
        
    def send_message(self, channel, message, sender=None):
        if channel in self.channels:
            for receiver in self.channels[channel]:
                if receiver != sender:
                    receiver.receive_message(message)
                    
    def register_widget(self, channel, widget):
        if channel in self.channels:
            self.channels[channel].append(widget)
            
    def unregister_widget(self, channel, widget):
        if channel in self.channels and widget in self.channels[channel]:
            self.channels[channel].remove(widget)
