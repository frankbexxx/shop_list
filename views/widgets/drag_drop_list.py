from kivy.uix.recycleview import RecycleView
from kivy.properties import BooleanProperty, NumericProperty
from kivy.animation import Animation
from kivy.metrics import dp

class DragAndDropList(RecycleView):
    dragging = BooleanProperty(False)
    drag_index = NumericProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.effect_cls = None  # Disable scroll effect during drag
        self.drag_start_y = 0
        self.original_index = None
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.drag_start_y = touch.y
            for idx, item in enumerate(self.data):
                if self._item_at_position(touch.y, idx):
                    self.drag_index = idx
                    self.original_index = idx
                    self.dragging = True
                    return True
        return super().on_touch_down(touch)
        
    def on_touch_move(self, touch):
        if self.dragging:
            current_y = touch.y
            new_index = self._get_index_at_pos(current_y)
            
            if new_index != self.drag_index:
                self._swap_items(self.drag_index, new_index)
                self.drag_index = new_index
            return True
        return super().on_touch_move(touch)
        
    def on_touch_up(self, touch):
        if self.dragging:
            self.dragging = False
            self._animate_item_to_position(self.drag_index)
            return True
        return super().on_touch_up(touch)
        
    def _swap_items(self, old_index, new_index):
        self.data[old_index], self.data[new_index] = \
            self.data[new_index], self.data[old_index]
