"""Base classes for entity component system."""
from typing import Dict, Type, TypeVar, Optional, List, Tuple
import pygame

T = TypeVar('T', bound='Component')

class Entity:
    """Base class for all game entities."""
    
    def __init__(self, game):
        """Initialize the entity with a reference to the game instance."""
        self.game = game
        self.components: Dict[str, 'Component'] = {}
    
    def add_component(self, component_type: Type[T], *args, **kwargs) -> T:
        """Add a component to the entity."""
        component = component_type(self, *args, **kwargs)
        name = component_type.__name__.lower().replace('component', '')
        self.components[name] = component
        return component
    
    def get_component(self, name: str) -> Optional['Component']:
        """Get a component by name."""
        return self.components.get(name.lower().replace('component', ''))
    
    def update(self, dt: float):
        """Update all components of the entity."""
        for component in self.components.values():
            component.update(dt)

class Component:
    """Base class for all components."""
    
    def __init__(self, entity: Entity):
        """Initialize the component with a reference to its entity."""
        self.entity = entity
    
    def update(self, dt: float):
        """Update the component's state."""
        pass

class TransformComponent(Component):
    """Component for handling position and movement."""
    
    def __init__(self, entity: Entity, x: float = 0, y: float = 0):
        """Initialize the transform component with position and velocity."""
        super().__init__(entity)
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0.0  # Rotation in degrees
    
    def update(self, dt: float):
        """Update position based on velocity."""
        self.position += self.velocity * dt

class RenderComponent(Component):
    """Component for rendering entities."""
    
    def __init__(self, entity: Entity):
        """Initialize the render component."""
        super().__init__(entity)
        self.color = (255, 255, 255)  # Default white
        self.vertices: List[Tuple[float, float]] = []
        self.visible = True
    
    def draw(self, screen: pygame.Surface):
        """Draw the entity on the screen."""
        if not self.visible or len(self.vertices) < 2:
            return
            
        transform = self.entity.get_component('transform')
        if not transform:
            return
            
        # Convert local vertices to world space
        world_vertices = []
        for vertex in self.vertices:
            # Rotate vertex
            x = vertex[0] * pygame.math.cos(pygame.math.radians(transform.rotation)) - \
                vertex[1] * pygame.math.sin(pygame.math.radians(transform.rotation))
            y = vertex[0] * pygame.math.sin(pygame.math.radians(transform.rotation)) + \
                vertex[1] * pygame.math.cos(pygame.math.radians(transform.rotation))
            
            # Translate to world position
            world_x = x + transform.position.x
            world_y = y + transform.position.y
            world_vertices.append((world_x, world_y))
        
        # Draw lines between vertices
        if len(world_vertices) == 2:  # Line (for bullets)
            pygame.draw.line(screen, self.color, world_vertices[0], world_vertices[1])
        else:  # Polygon (for ship and asteroids)
            pygame.draw.polygon(screen, self.color, world_vertices, 1)

class CollisionComponent(Component):
    """Component for handling collisions."""
    
    def __init__(self, entity: Entity, radius: float):
        """Initialize the collision component with a radius."""
        super().__init__(entity)
        self.radius = radius
        self.active = True
    
    def check_collision(self, other: 'CollisionComponent') -> bool:
        """Check for collision with another collision component."""
        if not self.active or not other.active:
            return False
            
        transform = self.entity.get_component('transform')
        other_transform = other.entity.get_component('transform')
        
        if not transform or not other_transform:
            return False
        
        distance = transform.position.distance_to(other_transform.position)
        return distance < (self.radius + other.radius) 