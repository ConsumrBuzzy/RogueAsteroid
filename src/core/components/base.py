"""Base component classes for the game engine."""
from typing import Any, Optional, Tuple, Dict, List, Callable
import pygame
from pygame import Surface, Rect, Vector2

class Component:
    """Base class for all components."""
    
    def __init__(self, entity: Any):
        """Initialize the component.
        
        Args:
            entity: The entity this component belongs to
        """
        self.entity = entity
        self._active = True
        self.enabled = True
    
    @property
    def active(self) -> bool:
        """Check if component is active.
        
        Returns:
            True if component is active and enabled
        """
        return self._active and self.enabled
        
    @active.setter
    def active(self, value: bool) -> None:
        """Set component active state.
        
        Args:
            value: New active state
        """
        self._active = value
    
    def update(self, dt: float) -> None:
        """Update the component's state.
        
        Args:
            dt: Time elapsed since last update in seconds
        """
        pass
    
    def draw(self, surface: Surface) -> None:
        """Draw the component.
        
        Args:
            surface: Surface to draw on
        """
        pass
    
    def cleanup(self) -> None:
        """Clean up any resources used by the component."""
        pass

class TransformComponent(Component):
    """Component for position and rotation."""
    
    def __init__(self, entity: Any, x: float = 0, y: float = 0, rotation: float = 0):
        """Initialize the transform component.
        
        Args:
            entity: The entity this component belongs to
            x: Initial x position
            y: Initial y position
            rotation: Initial rotation in degrees
        """
        super().__init__(entity)
        self.x = x
        self.y = y
        self.rotation = rotation
        self.velocity = Vector2(0.0, 0.0)
    
    def get_position(self) -> Tuple[float, float]:
        """Get the current position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self.y)
    
    def set_position(self, x: float, y: float) -> None:
        """Set the position.
        
        Args:
            x: New x position
            y: New y position
        """
        self.x = x
        self.y = y
        
    def update(self, dt: float) -> None:
        """Update position based on velocity.
        
        Args:
            dt: Time elapsed since last update in seconds
        """
        if self.velocity.length() > 0:
            self.x += self.velocity.x * dt
            self.y += self.velocity.y * dt

class RenderComponent(Component):
    """Component for rendering entities."""
    
    def __init__(self, entity: Any, color: Tuple[int, int, int] = (255, 255, 255),
                 points: Optional[List[Tuple[float, float]]] = None):
        """Initialize the render component.
        
        Args:
            entity: The entity this component belongs to
            color: RGB color tuple
            points: List of points defining the shape to render
        """
        super().__init__(entity)
        self.color = color
        self.points = points or []
        self.visible = True
    
    def draw(self, surface: Surface) -> None:
        """Draw the entity on the surface.
        
        Args:
            surface: Surface to draw on
        """
        if not self.visible or not self.points:
            return
            
        transform = self.entity.get_component('TransformComponent')
        if not transform:
            return
            
        # Transform points based on entity position and rotation
        transformed_points = []
        for x, y in self.points:
            # Rotate point
            angle = -transform.rotation * (3.14159 / 180)
            rotated_x = x * pygame.math.cos(angle) - y * pygame.math.sin(angle)
            rotated_y = x * pygame.math.sin(angle) + y * pygame.math.cos(angle)
            # Translate point
            transformed_points.append((
                rotated_x + transform.x,
                rotated_y + transform.y
            ))
        
        # Draw the shape
        if len(transformed_points) > 2:
            pygame.draw.polygon(surface, self.color, transformed_points)
        elif len(transformed_points) == 2:
            pygame.draw.line(surface, self.color, transformed_points[0], transformed_points[1])
        else:
            pygame.draw.circle(surface, self.color, transformed_points[0], 1)

class CollisionComponent(Component):
    """Component for collision detection."""
    
    def __init__(self, entity: Any, radius: float):
        """Initialize the collision component.
        
        Args:
            entity: The entity this component belongs to
            radius: Collision radius
        """
        super().__init__(entity)
        self.radius = radius
        self.colliding = False
    
    def get_collision_rect(self) -> Rect:
        """Get the collision rectangle.
        
        Returns:
            Pygame Rect for collision detection
        """
        transform = self.entity.get_component('TransformComponent')
        if not transform:
            return pygame.Rect(0, 0, 0, 0)
            
        return pygame.Rect(
            transform.x - self.radius,
            transform.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

class InputComponent(Component):
    """Component for handling entity input."""
    
    def __init__(self, entity: Any):
        """Initialize the input component.
        
        Args:
            entity: The entity this component belongs to
        """
        super().__init__(entity)
        self._action_bindings: Dict[str, List[int]] = {}  # Action name -> key list
        self._action_handlers: Dict[str, Callable[[], None]] = {}  # Action name -> handler
    
    def bind_action(self, action: str, keys: List[int], handler: Callable[[], None]) -> None:
        """Bind an action to keys and handler.
        
        Args:
            action: Name of the action
            keys: List of pygame key constants
            handler: Function to call when action is triggered
        """
        self._action_bindings[action] = keys
        self._action_handlers[action] = handler
    
    def clear_bindings(self) -> None:
        """Clear all action bindings."""
        self._action_bindings.clear()
        self._action_handlers.clear()
    
    def update(self, dt: float) -> None:
        """Check for input and trigger actions.
        
        Args:
            dt: Time elapsed since last update in seconds
        """
        if not self.active:
            return
            
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Check each action
        for action, bound_keys in self._action_bindings.items():
            # If any bound key is pressed
            if any(keys[key] for key in bound_keys):
                handler = self._action_handlers.get(action)
                if handler:
                    handler()

class ScreenWrapComponent(Component):
    """Component for wrapping entities around screen edges."""
    
    def update(self, dt: float) -> None:
        """Update the entity's position to wrap around screen edges.
        
        Args:
            dt: Time elapsed since last update in seconds
        """
        if not self.active:
            return
            
        transform = self.entity.get_component('TransformComponent')
        if not transform:
            return
            
        from ..constants import SCREEN_WIDTH, SCREEN_HEIGHT
        
        # Wrap horizontally
        if transform.x < 0:
            transform.x = SCREEN_WIDTH
        elif transform.x > SCREEN_WIDTH:
            transform.x = 0
            
        # Wrap vertically
        if transform.y < 0:
            transform.y = SCREEN_HEIGHT
        elif transform.y > SCREEN_HEIGHT:
            transform.y = 0 