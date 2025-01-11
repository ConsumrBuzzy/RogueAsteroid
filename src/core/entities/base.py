"""Base classes for entity component system.

This module provides the foundational classes for the entity component system (ECS).
The system is designed to be flexible, extensible, and maintainable, following SOLID principles.
"""

from typing import Dict, Type, TypeVar, Optional, List, Tuple, Any
import pygame
import math
from pygame import Vector2
import numpy as np

T = TypeVar('T', bound='Component')

class Entity:
    """Base class for all game entities.
    
    An entity is a container for components that define its behavior and properties.
    Each entity has a unique set of components that can be added, retrieved, and updated.
    """
    
    def __init__(self, game: Any) -> None:
        """Initialize the entity with a reference to the game instance.
        
        Args:
            game: The game instance this entity belongs to.
        """
        self._game = game
        self._components: Dict[str, 'Component'] = {}
    
    @property
    def game(self) -> Any:
        """Get the game instance this entity belongs to."""
        return self._game
    
    def add_component(self, component_type: Type[T], *args: Any, **kwargs: Any) -> T:
        """Add a component to the entity.
        
        Args:
            component_type: The type of component to add.
            *args: Positional arguments for component initialization.
            **kwargs: Keyword arguments for component initialization.
            
        Returns:
            The newly created component instance.
            
        Raises:
            ValueError: If a component of the same type already exists.
        """
        name = component_type.__name__.lower().replace('component', '')
        if name in self._components:
            raise ValueError(f"Component {name} already exists on this entity")
            
        component = component_type(self, *args, **kwargs)
        self._components[name] = component
        return component
    
    def get_component(self, name: str) -> Optional['Component']:
        """Get a component by name.
        
        Args:
            name: The name of the component to retrieve.
            
        Returns:
            The component if found, None otherwise.
        """
        return self._components.get(name.lower().replace('component', ''))
    
    def update(self, dt: float) -> None:
        """Update all components of the entity.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        for component in self._components.values():
            component.update(dt)

class Component:
    """Base class for all components.
    
    Components define specific behaviors and properties that can be attached to entities.
    Each component should have a single responsibility following the Single Responsibility Principle.
    """
    
    def __init__(self, entity: Entity) -> None:
        """Initialize the component with a reference to its entity.
        
        Args:
            entity: The entity this component belongs to.
        """
        self._entity = entity
    
    @property
    def entity(self) -> Entity:
        """Get the entity this component belongs to."""
        return self._entity
    
    def update(self, dt: float) -> None:
        """Update the component's state.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        pass

class TransformComponent(Component):
    """Component for handling position and movement.
    
    Manages an entity's position, velocity, and rotation in 2D space.
    """
    
    def __init__(self, entity: Entity, x: float = 0, y: float = 0) -> None:
        """Initialize the transform component.
        
        Args:
            entity: The entity this component belongs to.
            x: Initial x position.
            y: Initial y position.
        """
        super().__init__(entity)
        self._position = Vector2(float(x), float(y))
        self._velocity = Vector2(0, 0)
        self._rotation = 0.0  # Rotation in degrees
        self._rotation_speed = 0.0  # Rotation speed in degrees per second
    
    @property
    def position(self) -> Vector2:
        """Get the current position."""
        return self._position
        
    @position.setter
    def position(self, value) -> None:
        """Set the current position."""
        if isinstance(value, (list, tuple, np.ndarray)):
            self._position = Vector2(float(value[0]), float(value[1]))
        else:
            self._position = Vector2(value)
    
    @property
    def velocity(self) -> Vector2:
        """Get the current velocity."""
        return self._velocity
        
    @velocity.setter
    def velocity(self, value) -> None:
        """Set the current velocity."""
        if isinstance(value, (list, tuple, np.ndarray)):
            self._velocity = Vector2(float(value[0]), float(value[1]))
        else:
            self._velocity = Vector2(value)
    
    @property
    def rotation(self) -> float:
        """Get the current rotation in degrees."""
        return self._rotation
        
    @rotation.setter
    def rotation(self, value: float) -> None:
        """Set the current rotation in degrees."""
        self._rotation = value % 360.0
    
    @property
    def rotation_speed(self) -> float:
        """Get the current rotation speed in degrees per second."""
        return self._rotation_speed
        
    @rotation_speed.setter
    def rotation_speed(self, value: float) -> None:
        """Set the current rotation speed in degrees per second."""
        self._rotation_speed = value
    
    def update(self, dt: float) -> None:
        """Update position based on velocity and rotation based on rotation speed.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        self._position += self._velocity * dt
        self._rotation = (self._rotation + self._rotation_speed * dt) % 360.0

class RenderComponent(Component):
    """Component for rendering entities.
    
    Handles the visual representation of an entity, including its shape, color,
    and visibility state. Supports both line and polygon rendering.
    """
    
    def __init__(self, entity: Entity) -> None:
        """Initialize the render component.
        
        Args:
            entity: The entity this component belongs to.
        """
        super().__init__(entity)
        self._color = (255, 255, 255)  # Default white
        self._vertices: List[Tuple[float, float]] = []
        self._visible = True
    
    @property
    def color(self) -> Tuple[int, int, int]:
        """Get the current color."""
        return self._color
        
    @color.setter
    def color(self, value: Tuple[int, int, int]) -> None:
        """Set the current color."""
        self._color = value
    
    @property
    def vertices(self) -> List[Tuple[float, float]]:
        """Get the current vertices."""
        return self._vertices
        
    @vertices.setter
    def vertices(self, value: List[Tuple[float, float]]) -> None:
        """Set the current vertices."""
        self._vertices = value
    
    @property
    def visible(self) -> bool:
        """Get the current visibility state."""
        return self._visible
        
    @visible.setter
    def visible(self, value: bool) -> None:
        """Set the current visibility state."""
        self._visible = value
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the entity on the screen.
        
        Args:
            screen: The pygame surface to draw on.
        """
        if not self._visible or len(self._vertices) < 2:
            return
            
        transform = self.entity.get_component('transform')
        if not transform:
            return
            
        # Convert local vertices to world space
        world_vertices = self._get_world_vertices(transform)
        
        # Draw lines between vertices
        if len(world_vertices) == 2:  # Line (for bullets)
            pygame.draw.line(screen, self._color, world_vertices[0], world_vertices[1])
        else:  # Polygon (for ship and asteroids)
            pygame.draw.polygon(screen, self._color, world_vertices, 1)
    
    def _get_world_vertices(self, transform: TransformComponent) -> List[Tuple[float, float]]:
        """Convert local vertices to world space.
        
        Args:
            transform: The transform component to use for the conversion.
            
        Returns:
            List of vertices in world space.
        """
        world_vertices = []
        rotation_rad = math.radians(transform.rotation)
        cos_rot = math.cos(rotation_rad)
        sin_rot = math.sin(rotation_rad)
        
        for vertex in self._vertices:
            # Rotate vertex
            x = vertex[0] * cos_rot - vertex[1] * sin_rot
            y = vertex[0] * sin_rot + vertex[1] * cos_rot
            
            # Translate to world position
            world_x = x + transform.position.x
            world_y = y + transform.position.y
            world_vertices.append((world_x, world_y))
            
        return world_vertices

class CollisionComponent(Component):
    """Component for handling collisions.
    
    Manages collision detection between entities using circular collision bounds.
    """
    
    def __init__(self, entity: Entity, radius: float) -> None:
        """Initialize the collision component.
        
        Args:
            entity: The entity this component belongs to.
            radius: Radius of the collision circle.
        """
        super().__init__(entity)
        self._radius = radius
        self._active = True
    
    @property
    def radius(self) -> float:
        """Get the collision radius."""
        return self._radius
        
    @radius.setter
    def radius(self, value: float) -> None:
        """Set the collision radius."""
        self._radius = value
    
    @property
    def active(self) -> bool:
        """Get the collision active state."""
        return self._active
        
    @active.setter
    def active(self, value: bool) -> None:
        """Set the collision active state."""
        self._active = value
    
    def check_collision(self, other: 'CollisionComponent') -> bool:
        """Check for collision with another collision component.
        
        Args:
            other: The other collision component to check against.
            
        Returns:
            True if the components are colliding, False otherwise.
        """
        if not (self._active and other._active):
            return False
            
        transform = self.entity.get_component('transform')
        other_transform = other.entity.get_component('transform')
        
        if not (transform and other_transform):
            return False
            
        distance = transform.position.distance_to(other_transform.position)
        return distance <= (self._radius + other._radius)
    
    def get_collision_normal(self, other: 'CollisionComponent') -> Optional[Vector2]:
        """Get the collision normal vector between this and another component.
        
        Args:
            other: The other collision component.
            
        Returns:
            Normalized vector pointing from other to this component, or None if not colliding.
        """
        if not self.check_collision(other):
            return None
            
        transform = self.entity.get_component('transform')
        other_transform = other.entity.get_component('transform')
        
        if not (transform and other_transform):
            return None
            
        # Get vector from other to this
        normal = transform.position - other_transform.position
        if normal.length() > 0:
            normal.normalize_ip()
            return normal
        return Vector2(1, 0)  # Default direction if positions are identical
    
    def get_collision_depth(self, other: 'CollisionComponent') -> float:
        """Get the overlap depth between this and another component.
        
        Args:
            other: The other collision component.
            
        Returns:
            The overlap depth, or 0 if not colliding.
        """
        if not self.check_collision(other):
            return 0.0
            
        transform = self.entity.get_component('transform')
        other_transform = other.entity.get_component('transform')
        
        if not (transform and other_transform):
            return 0.0
            
        distance = transform.position.distance_to(other_transform.position)
        return self._radius + other._radius - distance 