from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, ObjectProperty
from kivy.metrics import dp

class ColorThemeSelector(BoxLayout):
    current_theme = DictProperty()
    themes = DictProperty({
        'light': {
            'primary': '#2196F3',
            'secondary': '#FF9800',
            'background': '#FFFFFF',
            'text': '#000000'
        },
        'dark': {
            'primary': '#1976D2',
            'secondary': '#F57C00',
            'background': '#121212',
            'text': '#FFFFFF'
        },
        'nature': {
            'primary': '#4CAF50',
            'secondary': '#8BC34A',
            'background': '#F1F8E9',
            'text': '#1B5E20'
        }
    })
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(15)
        self._setup_layout()
        
    def _setup_layout(self):
        for theme_name, colors in self.themes.items():
            theme_btn = ThemeButton(
                text=theme_name.title(),
                colors=colors,
                size_hint_y=None,
                height=dp(50)
            )
            theme_btn.bind(on_release=lambda btn: self._select_theme(btn.colors))
            self.add_widget(theme_btn)
            
    def _select_theme(self, theme_colors):
        self.current_theme = theme_colors
