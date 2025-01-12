"""Screen wrap component module."""
from .base import Component
from .transform import TransformComponent

class ScreenWrapComponent(Component):
    """Component for wrapping entities around screen edges."""
    def __init__(self, entity):
        super().__init__(entity)
        self.wrap_x = True
        self.wrap_y = True
        self.buffer = 0  # Extra space before wrapping
    
    def update(self, dt: float) -> None:
        """Update screen wrapping."""
        transform = self.entity.get_component(TransformComponent)
        if not transform:
            return
        
        # Get screen dimensions from game instance
        width = self.entity.game.width
        height = self.entity.game.height
        
        # Wrap position
        if self.wrap_x:
            if transform.position.x < -self.buffer:
                transform.position.x = width + self.buffer
            elif transform.position.x > width + self.buffer:
                transform.position.x = -self.buffer
        
        if self.wrap_y:
            if transform.position.y < -self.buffer:
                transform.position.y = height + self.buffer
            elif transform.position.y > height + self.buffer:
                transform.position.y = -self.buffer 