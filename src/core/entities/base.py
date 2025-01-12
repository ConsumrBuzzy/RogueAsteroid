"""Base classes for entity component system."""
from typing import Optional, Type, TypeVar, List, Union, Any
import pygame

T = TypeVar('T', bound='Component')

class Component:
    """Base class for all components."""
    
    def __init__(self, entity: 'Entity', **kwargs):
        """Initialize the component.
        
        Args:
            entity: The entity this component belongs to
            **kwargs: Additional initialization parameters
        """
        self.entity = entity
        self.active = True
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the component after all components are added."""
        if self._initialized:
            return
        self._initialized = True
    
    def update(self, dt: float) -> None:
        """Update the component.
        
        Args:
            dt: Time delta in seconds
        """
        pass
    
    def destroy(self) -> None:
        """Clean up the component."""
        self.active = False
        self._initialized = False
        
    def get_component(self, component_type: type) -> Any:
        """Get another component from the parent entity.
        
        Args:
            component_type: The type of component to get
            
        Returns:
            The component instance if found, None otherwise
        """
        return self.entity.get_component(component_type)

class Entity:
    """Base class for all game entities."""
    
    def __init__(self, game):
        """Initialize the entity.
        
        Args:
            game: The game instance
        """
        self.game = game
        self.components: List[Component] = []
        self.active = True
        self._initialized = False
    
    def add_component(self, component_or_type: Union[Component, Type[T]], *args, **kwargs) -> T:
        """Add a component to the entity.
        
        Args:
            component_or_type: Component instance or type to add
            *args: Positional arguments for component initialization
            **kwargs: Keyword arguments for component initialization
            
        Returns:
            The added component
            
        Raises:
            TypeError: If component_or_type is not a Component instance or type
        """
        if isinstance(component_or_type, Component):
            component = component_or_type
        elif isinstance(component_or_type, type) and issubclass(component_or_type, Component):
            component = component_or_type(self, *args, **kwargs)
        else:
            raise TypeError("component_or_type must be a Component instance or type")
            
        self.components.append(component)
        return component
    
    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """Get a component of the specified type.
        
        Args:
            component_type: The type of component to get
            
        Returns:
            The component if found, None otherwise
        """
        for component in self.components:
            if isinstance(component, component_type):
                return component
        return None
    
    def remove_component(self, component: Component) -> None:
        """Remove a component from the entity.
        
        Args:
            component: The component to remove
        """
        if component in self.components:
            component.destroy()
            self.components.remove(component)
    
    def initialize(self) -> None:
        """Initialize the entity and all its components."""
        if not self._initialized:
            for component in self.components:
                component.initialize()
            self._initialized = True
    
    def update(self, dt: float) -> None:
        """Update the entity and all its components.
        
        Args:
            dt: Time delta in seconds
        """
        if self.active and self._initialized:
            for component in self.components:
                if component.active:
                    component.update(dt)
    
    def destroy(self) -> None:
        """Clean up the entity and all its components."""
        for component in self.components[:]:  # Copy list to avoid modification during iteration
            self.remove_component(component)
        self.active = False

class TransformComponent(Component):
    """Component for position, rotation, and movement."""
    
    def __init__(self, entity: Entity):
        """Initialize the transform component.
        
        Args:
            entity: The entity this component belongs to
        """
        super().__init__(entity)
        self.position = pygame.Vector2(0.0, 0.0)
        self.velocity = pygame.Vector2(0.0, 0.0)
        self.rotation = 0.0
        self.rotation_speed = 0.0
    
    def update(self, dt: float) -> None:
        """Update position and rotation.
        
        Args:
            dt: Time delta in seconds
        """
        if self.active:
            self.position += self.velocity * dt
            self.rotation += self.rotation_speed * dt

class RenderComponent(Component):
    """Component for rendering entities."""
    
    def __init__(self, entity: Entity):
        """Initialize the render component.
        
        Args:
            entity: The entity this component belongs to
        """
        super().__init__(entity)
        self.vertices = []
        self.color = (255, 255, 255)
        self.visible = True
    
    def update(self, dt: float) -> None:
        """Update rendering state.
        
        Args:
            dt: Time delta in seconds
        """
        pass

class CollisionComponent(Component):
    """Component for collision detection."""
    
    def __init__(self, entity: Entity, radius: float = 1.0):
        """Initialize the collision component.
        
        Args:
            entity: The entity this component belongs to
            radius: Collision radius
        """
        super().__init__(entity)
        self.radius = radius
    
    def check_collision(self, other: 'CollisionComponent') -> bool:
        """Check for collision with another collision component.
        
        Args:
            other: The other collision component to check against
            
        Returns:
            True if colliding, False otherwise
        """
        if not (self.active and other.active):
            return False
            
        transform = self.entity.get_component(TransformComponent)
        other_transform = other.entity.get_component(TransformComponent)
        
        if not (transform and other_transform):
            return False
            
        distance = transform.position.distance_to(other_transform.position)
        return distance <= (self.radius + other.radius)
    
    def get_collision_normal(self, other: 'CollisionComponent') -> pygame.Vector2:
        """Get the collision normal vector between this and another component.
        
        Args:
            other: The other collision component
            
        Returns:
            The normalized vector pointing from other to this
        """
        transform = self.entity.get_component(TransformComponent)
        other_transform = other.entity.get_component(TransformComponent)
        
        if not (transform and other_transform):
            return pygame.Vector2(0, 0)
            
        normal = transform.position - other_transform.position
        if normal.length() > 0:
            normal.normalize_ip()
        return normal 