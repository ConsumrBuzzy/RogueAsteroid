"""Base entity system using component-based architecture."""
from typing import List, Set, Type, Dict, Any, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from src.core.game import Game

class Component:
    """Base class for all entity components."""
    
    def __init__(self, entity: 'Entity'):
        self.entity = entity
        self.active = True
    
    def update(self, dt: float) -> None:
        """Update component state."""
        pass
    
    def draw(self, surface: Any) -> None:
        """Draw component if it has visual elements."""
        pass

class TransformComponent(Component):
    """Handles position, rotation, and movement."""
    
    def __init__(self, entity: 'Entity', x: float = 0, y: float = 0):
        super().__init__(entity)
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.array([0.0, 0.0], dtype=float)
        self.rotation = 0.0  # degrees
    
    def update(self, dt: float) -> None:
        """Update position based on velocity."""
        self.position += self.velocity * dt

class RenderComponent(Component):
    """Handles entity rendering."""
    
    def __init__(self, entity: 'Entity'):
        super().__init__(entity)
        self.color = (255, 255, 255)  # default white
        self.vertices: List[tuple[float, float]] = []
        self.visible = True
    
    def draw(self, surface: Any) -> None:
        """Draw the entity using its vertices."""
        if not self.visible or not self.vertices:
            return
            
        import pygame
        transformed = self._get_transformed_vertices()
        pygame.draw.lines(surface, self.color, True, transformed)
    
    def _get_transformed_vertices(self) -> List[tuple[float, float]]:
        """Get vertices transformed by entity's position and rotation."""
        transform = self.entity.get_component(TransformComponent)
        if not transform:
            return self.vertices
            
        angle_rad = np.radians(transform.rotation)
        cos_rot = np.cos(angle_rad)
        sin_rot = np.sin(angle_rad)
        
        transformed = []
        for x, y in self.vertices:
            # Rotate
            rx = x * cos_rot - y * sin_rot
            ry = x * sin_rot + y * cos_rot
            # Translate
            rx += transform.position[0]
            ry += transform.position[1]
            transformed.append((rx, ry))
            
        return transformed

class CollisionComponent(Component):
    """Handles collision detection."""
    
    def __init__(self, entity: 'Entity', radius: float = 1.0):
        super().__init__(entity)
        self.radius = radius
    
    def collides_with(self, other: 'CollisionComponent') -> bool:
        """Check for collision with another entity."""
        transform = self.entity.get_component(TransformComponent)
        other_transform = other.entity.get_component(TransformComponent)
        
        if not transform or not other_transform:
            return False
            
        distance = np.linalg.norm(transform.position - other_transform.position)
        return distance < (self.radius + other.radius)

class Entity:
    """Base class for all game entities using component system."""
    
    def __init__(self, game: 'Game'):
        self.game = game
        self.active = True
        self._components: Dict[Type[Component], Component] = {}
    
    def add_component(self, component_class: Type[Component], *args, **kwargs) -> Component:
        """Add a component to the entity."""
        component = component_class(self, *args, **kwargs)
        self._components[component_class] = component
        return component
    
    def get_component(self, component_class: Type[Component]) -> Component:
        """Get a component by its class."""
        return self._components.get(component_class)
    
    def has_component(self, component_class: Type[Component]) -> bool:
        """Check if entity has a specific component."""
        return component_class in self._components
    
    def update(self, dt: float) -> None:
        """Update all components."""
        for component in self._components.values():
            if component.active:
                component.update(dt)
    
    def draw(self, surface: Any) -> None:
        """Draw all components."""
        render = self.get_component(RenderComponent)
        if render and render.active:
            render.draw(surface) 