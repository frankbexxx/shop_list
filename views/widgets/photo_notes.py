from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty
from kivy.metrics import dp

class PhotoNotes(BoxLayout):
    photos = ListProperty([])
    current_note = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(12)
        self._setup_photo_notes()
        
    def _setup_photo_notes(self):
        # Camera preview
        self.camera_preview = CameraPreview(
            size_hint_y=0.4
        )
        
        # Photo gallery
        self.photo_gallery = PhotoGallery(
            size_hint_y=0.3
        )
        
        # Notes editor
        self.notes_editor = NotesEditor(
            size_hint_y=0.2
        )
        
        # Control buttons
        self.controls = PhotoControls(
            size_hint_y=0.1
        )
        
        self.add_widget(self.camera_preview)
        self.add_widget(self.photo_gallery)
        self.add_widget(self.notes_editor)
        self.add_widget(self.controls)
