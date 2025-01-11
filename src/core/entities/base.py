"""Base classes for entity component system."""
from typing import Dict, Type, TypeVar, Optional, Any
import numpy as np
import pygame  # Add at top level to avoid circular import

T = TypeVar('T', bound='Component')

class Component:
    """Base class for all components."""
    
    def __init__(self, entity: 'Entity'):
        self.entity = entity
    
    def update(self, dt: float) -> None:
        """Update component state."""
        pass

class Entity:
    """Base class for all game entities."""
    
    def __init__(self, game: Any):
        self.game = game
        self.components: Dict[str, Component] = {}
    
    def add_component(self, component_type: Type[T], *args, **kwargs) -> T:
        """Add a component to the entity."""
        component = component_type(self, *args, **kwargs)
        self.components[component_type.__name__.lower()] = component
        return component
    
    def get_component(self, component_name: str) -> Optional[Component]:
        """Get a component by name."""
        return self.components.get(component_name.lower())
    
    def update(self, dt: float) -> None:
        """Update all components."""
        for component in self.components.values():
            component.update(dt)

class TransformComponent(Component):
    """Component for position and movement."""
    
    def __init__(self, entity: Entity, x: float, y: float):
        super().__init__(entity)
        self.position = np.array([float(x), float(y)])
        self.velocity = np.array([0.0, 0.0])
        self.rotation = 0.0  # degrees
        self.rotation_speed = 0.0  # degrees per second
    
    def update(self, dt: float) -> None:
        """Update position based on velocity."""
        self.position += self.velocity * dt
        self.rotation += self.rotation_speed * dt

class RenderComponent(Component):
    """Component for rendering."""
    
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self.vertices = []  # List of (x, y) tuples
        self.color = (255, 255, 255)  # White default
        self.visible = True  # Default to visible
    
    def draw(self, surface: Any) -> None:
        """Draw the entity on the surface."""
        if not self.visible:
            return
            
        if not self.vertices:
            print(f"Warning: No vertices defined for {self.entity.__class__.__name__}")
            return
            
        transform = self.entity.get_component('transform')
        if not transform:
            print(f"Warning: No transform component for {self.entity.__class__.__name__}")
            return
            
        # Convert vertices to screen space
        screen_vertices = []
        for x, y in self.vertices:
            # Rotate point
            angle = np.radians(transform.rotation)
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            
            # Translate to position
            screen_x = transform.position[0] + rx
            screen_y = transform.position[1] + ry
            screen_vertices.append((int(screen_x), int(screen_y)))
        
        # Draw polygon
        if len(screen_vertices) >= 2:  # Allow lines (2 vertices) and polygons (3+ vertices)
            if len(screen_vertices) == 2:
                # Draw line for bullets
                pygame.draw.line(surface, self.color, screen_vertices[0], screen_vertices[1])
            else:
                # Draw polygon for ship and asteroids
                pygame.draw.polygon(surface, self.color, screen_vertices)
                
                # Debug: Draw center point
                center = (int(transform.position[0]), int(transform.position[1]))
                pygame.draw.circle(surface, (255, 0, 0), center, 2)

class CollisionComponent(Component):
    """Component for collision detection."""
    
    def __init__(self, entity: Entity, radius: float):
        super().__init__(entity)
        self.radius = radius
        self.active = True  # Can be disabled temporarily
    
    def check_collision(self, other: 'CollisionComponent') -> bool:
        """Check for collision with another entity."""
        if not self.active or not other.active:
            return False
            
        transform = self.entity.get_component('transform')
        other_transform = other.entity.get_component('transform')
        
        if not transform or not other_transform:
            return False
        
        # Calculate distance between centers
        distance = np.linalg.norm(
            transform.position - other_transform.position
        )
        
        # Check if circles overlap
        return distance < (self.radius + other.radius)
    
    def get_collision_normal(self, other: 'CollisionComponent') -> Optional[np.ndarray]:
        """Get the collision normal vector pointing from other to self."""
        transform = self.entity.get_component('transform')
        other_transform = other.entity.get_component('transform')
        
        if not transform or not other_transform:
            return None
        
        # Calculate vector from other to self
        delta = transform.position - other_transform.position
        distance = np.linalg.norm(delta)
        
        if distance == 0:
            # Objects are at same position, return arbitrary normal
            return np.array([1.0, 0.0])
            
        return delta / distance
    
    def get_collision_point(self, other: 'CollisionComponent') -> Optional[np.ndarray]:
        """Get the approximate point of collision."""
        transform = self.entity.get_component('transform')
        other_transform = other.entity.get_component('transform')
        
        if not transform or not other_transform:
            return None
        
        # Calculate point halfway between the objects at their radii
        normal = self.get_collision_normal(other)
        if normal is None:
            return None
            
        return transform.position - normal * self.radius 