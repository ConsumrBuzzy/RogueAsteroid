"""Base component classes for the game engine."""
from typing import Any, Optional, Tuple
import pygame
from pygame import Surface, Rect

class Component:
    """Base class for all components."""
    
    def __init__(self, entity: Any):
        """Initialize the component.
        
        Args:
            entity: The entity this component belongs to
        """
        self.entity = entity
        self.active = True
    
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

class RenderComponent(Component):
    """Component for rendering entities."""
    
    def __init__(self, entity: Any, color: Tuple[int, int, int] = (255, 255, 255),
                 points: Optional[list[Tuple[float, float]]] = None):
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